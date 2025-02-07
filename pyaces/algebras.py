# =======================================

from __future__ import annotations
from .poly import Polynomial
from .compaces import read_operations, Algebra
from .aces import ACESCipher, ACESPseudoCipher, ACES, ACESReader, ArithChannel
from functools import reduce
from typing import Union, Optional, Callable, Tuple
import random
import pickle
import json
import os
import numpy as np

# =======================================


class ACESAlgebra(Algebra):
    def __init__(
        self,
        p: int,
        q: int,
        n: int,
        u: Polynomial,
        tensor: list[list[list[int]]],
        debug: bool = False,
        refresh_classifier: Optional[Callable[[ACESCipher], bool]] = None,
        encrypter: Optional[Union[ACES, ACESReader]] = None,
        refresher: Optional[list[ACESCipher]] = None,
        **args,
    ):
        self.p = p
        self.q = q
        self.n = n
        self.u = u
        self.tensor = tensor
        self.debug = debug
        self.refresh_classifier = refresh_classifier
        self.encrypter = encrypter
        self.refresher = refresher

    def add(self, a: ACESCipher, b: ACESCipher, refresh: bool = True) -> ACESCipher:
        noise = a.lvl + b.lvl + (2 * (self.p - 1)) // self.p
        total_noise = (self.q + 1) // self.p - 1

        if noise / total_noise >= 0.99:
            if self.debug:
                print(
                    f"\033[92mACESAlgebra.add: next operation will reach max. saturation, at {round(100 * noise / total_noise, 4)}% of max. noise level.\033[0m"
                )

            if (
                refresh
                and self.refresh_classifier is not None
                and self.encrypter is not None
                and self.refresher is not None
            ):
                # Refresh `a` if needed
                estimated_refresh_noise = self.assess_refresh_level(
                    refresher=self.refresher, corefresher=a.corefresher(self.encrypter)
                )
                if estimated_refresh_noise >= a.lvl:
                    if self.debug:
                        print(
                            f"\033[92mACESAlgebra.add(a, b): `a` does not need to be refreshed as refresh would increase saturation by \u0394 = +{round(100 * (estimated_refresh_noise - a.lvl) / total_noise, 4)}%\033[0m"
                        )
                    a_refreshed = a

                else:
                    refreshable = self.refresh_classifier(a)
                    if self.debug and not refreshable:
                        print(
                            "\033[92mACESAlgebra.add(a, b): `a` is not refreshable!\033[0m"
                        )

                    a_ = None
                    while not refreshable:
                        neutral = self.encrypter.encrypt(0)
                        a_ = self.add(a, neutral, refresh=False)
                        refreshable = self.refresh_classifier(a_)
                        if refreshable:
                            break

                    if a_ is not None:
                        if self.debug:
                            print(
                                "\033[92mACESAlgebra.add(a, b): `a` is now refreshable.\033[0m"
                            )
                        a_refreshed = self.refresh(
                            refresher=self.refresher,
                            corefresher=a_.corefresher(self.encrypter),
                        )
                        if self.debug:
                            sat_evolution = f"{round(100 * a.lvl / total_noise, 4)}% -> {round(100 * a_.lvl / total_noise, 4)}% -> {round(100 * a_refreshed.lvl / total_noise, 4)}%"
                            print(
                                f"\033[92mACESAlgebra.add(a, b): `a` was successfully refreshed: {sat_evolution}.\033[0m"
                            )
                    else:
                        a_refreshed = self.refresh(
                            refresher=self.refresher,
                            corefresher=a.corefresher(self.encrypter),
                        )
                        if self.debug:
                            sat_evolution = f"{round(100 * a.lvl / total_noise, 4)}% -> {round(100 * a_refreshed.lvl / total_noise, 4)}%"
                            print(
                                f"\033[92mACESAlgebra.add(a, b): `a` was successfully refreshed: {sat_evolution}.\033[0m"
                            )

                # Refresh `b` if needed
                estimated_refresh_noise = self.assess_refresh_level(
                    refresher=self.refresher, corefresher=b.corefresher(self.encrypter)
                )
                if estimated_refresh_noise >= b.lvl:
                    if self.debug:
                        print(
                            f"\033[92mACESAlgebra.add(a, b): `b` does not need to be refreshed as refresh would increase saturation by \u0394 = +{round(100 * (estimated_refresh_noise - b.lvl) / total_noise, 4)}%\033[0m"
                        )
                    b_refreshed = b

                else:
                    refreshable = self.refresh_classifier(b)
                    if self.debug and not refreshable:
                        print(
                            "\033[92mACESAlgebra.add(a, b): `b` is not refreshable!\033[0m"
                        )

                    b_ = None
                    while not refreshable:
                        neutral = self.encrypter.encrypt(0)
                        b_ = self.add(b, neutral, refresh=False)
                        refreshable = self.refresh_classifier(b_)
                        if refreshable:
                            break

                    if b_ is not None:
                        if self.debug:
                            print(
                                "\033[92mACESAlgebra.add(a, b): `b` is now refreshable.\033[0m"
                            )
                        b_refreshed = self.refresh(
                            refresher=self.refresher,
                            corefresher=b_.corefresher(self.encrypter),
                        )
                        if self.debug:
                            sat_evolution = f"{round(100 * b.lvl / total_noise, 4)}% -> {round(100 * b_.lvl / total_noise, 4)}% -> {round(100 * b_refreshed.lvl / total_noise, 4)}%"
                            print(
                                f"\033[92mACESAlgebra.add(a, b): `b` was successfully refreshed: {sat_evolution}.\033[0m"
                            )
                    else:
                        b_refreshed = self.refresh(
                            refresher=self.refresher,
                            corefresher=b.corefresher(self.encrypter),
                        )
                        if self.debug:
                            sat_evolution = f"{round(100 * b.lvl / total_noise, 4)}% -> {round(100 * b_refreshed.lvl / total_noise, 4)}%"
                            print(
                                f"\033[92mACESAlgebra.add(a, b): `b` was successfully refreshed: {sat_evolution}.\033[0m"
                            )

                # Conclusion on refresh operations
                a_lvl = min(a.lvl, a_refreshed.lvl)
                b_lvl = min(b.lvl, b_refreshed.lvl)
                refreshed_noise = a_lvl + b_lvl + (2 * (self.p - 1)) // self.p

                if self.debug:
                    sat_delta = f"saturation of {round(100 * noise / total_noise, 4)}% by \u0394 = {round(100 * (refreshed_noise - noise) / total_noise, 4)}%"
                    print(
                        f"\033[94mACESAlgebra.add: refresh operation is to decrease {sat_delta}.\033[0m"
                    )

                if refreshed_noise / total_noise >= 0.99:
                    raise Exception(
                        f"ACESAlgebra.add: refresh operation failed due to saturation at {round(100 * refreshed_noise / total_noise, 4)}%"
                    )

                return self.add(
                    a_refreshed if a.lvl > a_refreshed.lvl else a,
                    b_refreshed if b.lvl > b_refreshed.lvl else b,
                    refresh=False,
                )

            else:
                raise Exception("ACESAlgebra.add: noise cannot be refreshed.")

        # Addition on ACES ciphertexts
        c0 = [(a.dec[k] + b.dec[k]) % self.u for k in range(self.n)]
        c1 = (a.enc + b.enc) % self.u

        if self.debug:
            total_noise = (self.q + 1) // self.p - 1
            input_saturation = f"({round(100 * a.lvl / total_noise, 4)}%, {round(100 * b.lvl / total_noise, 4)}%)"
            output_saturation = f"{round(100 * noise / total_noise, 4)}%"
            print(
                f"\033[93mWarning in ACESAlgebra.add: saturation increasing from {input_saturation} to {output_saturation} of max. noise level.\033[0m"
            )

        return ACESCipher(c0, c1, noise)

    def mult(self, a: ACESCipher, b: ACESCipher, refresh: bool = True) -> ACESCipher:
        noise = (a.lvl + b.lvl + a.lvl * b.lvl) * self.p + ((self.p - 1) ** 2) // self.p
        total_noise = (self.q + 1) // self.p - 1

        if noise / total_noise >= 0.99:
            if self.debug:
                print(
                    f"\033[95mACESAlgebra.mult: next operation will reach max. saturation at {round(100 * noise / total_noise, 4)}% of max. noise level.\033[0m"
                )

            if (
                refresh
                and self.refresh_classifier is not None
                and self.encrypter is not None
                and self.refresher is not None
            ):
                # Refresh `a` if needed
                estimated_refresh_noise = self.assess_refresh_level(
                    refresher=self.refresher, corefresher=a.corefresher(self.encrypter)
                )
                if estimated_refresh_noise >= a.lvl:
                    if self.debug:
                        print(
                            f"\033[92mACESAlgebra.mult(a, b): `a` does not need to be refreshed as refresh would increase saturation by \u0394 = +{round(100 * (estimated_refresh_noise - a.lvl) / total_noise, 4)}%\033[0m"
                        )
                    a_refreshed = a

                else:
                    refreshable = self.refresh_classifier(a)
                    if self.debug and not refreshable:
                        print(
                            "\033[92mACESAlgebra.mult(a, b): `a` is not refreshable!\033[0m"
                        )

                    a_ = None
                    while not refreshable:
                        neutral = self.encrypter.encrypt(0)
                        a_ = self.add(a, neutral, refresh=False)
                        refreshable = self.refresh_classifier(a_)
                        if refreshable:
                            break

                    if a_ is not None:
                        if self.debug:
                            print(
                                "\033[92mACESAlgebra.mult(a, b): `a` is now refreshable.\033[0m"
                            )
                        a_refreshed = self.refresh(
                            refresher=self.refresher,
                            corefresher=a_.corefresher(self.encrypter),
                        )
                        if self.debug:
                            sat_evolution = f"{round(100 * a.lvl / total_noise, 4)}% -> {round(100 * a_.lvl / total_noise, 4)}% -> {round(100 * a_refreshed.lvl / total_noise, 4)}%"
                            print(
                                f"\033[92mACESAlgebra.mult(a, b): `a` was successfully refreshed: {sat_evolution}.\033[0m"
                            )
                    else:
                        a_refreshed = self.refresh(
                            refresher=self.refresher,
                            corefresher=a.corefresher(self.encrypter),
                        )
                        if self.debug:
                            sat_evolution = f"{round(100 * a.lvl / total_noise, 4)}% -> {round(100 * a_refreshed.lvl / total_noise, 4)}%"
                            print(
                                f"\033[92mACESAlgebra.mult(a, b): `a` was successfully refreshed: {sat_evolution}.\033[0m"
                            )

                # Refresh `b` if needed
                estimated_refresh_noise = self.assess_refresh_level(
                    refresher=self.refresher, corefresher=b.corefresher(self.encrypter)
                )
                if estimated_refresh_noise >= b.lvl:
                    if self.debug:
                        print(
                            f"\033[92mACESAlgebra.mult(a, b): `b` does not need to be refreshed as refresh would increase saturation by \u0394 = +{round(100 * (estimated_refresh_noise - b.lvl) / total_noise, 4)}%\033[0m"
                        )
                    b_refreshed = b

                else:
                    refreshable = self.refresh_classifier(b)
                    if self.debug and not refreshable:
                        print(
                            "\033[92mACESAlgebra.mult(a, b): `b` is not refreshable!\033[0m"
                        )

                    b_ = None
                    while not refreshable:
                        neutral = self.encrypter.encrypt(0)
                        b_ = self.add(b, neutral, refresh=False)
                        refreshable = self.refresh_classifier(b_)
                        if refreshable:
                            break

                    if b_ is not None:
                        if self.debug:
                            print(
                                "\033[92mACESAlgebra.mult(a, b): `b` is now refreshable.\033[0m"
                            )
                        b_refreshed = self.refresh(
                            refresher=self.refresher,
                            corefresher=b_.corefresher(self.encrypter),
                        )
                        if self.debug:
                            sat_evolution = f"{round(100 * b.lvl / total_noise, 4)}% -> {round(100 * b_.lvl / total_noise, 4)}% -> {round(100 * b_refreshed.lvl / total_noise, 4)}%"
                            print(
                                f"\033[92mACESAlgebra.mult(a, b): `b` was successfully refreshed: {sat_evolution}.\033[0m"
                            )
                    else:
                        b_refreshed = self.refresh(
                            refresher=self.refresher,
                            corefresher=b.corefresher(self.encrypter),
                        )
                        if self.debug:
                            sat_evolution = f"{round(100 * b.lvl / total_noise, 4)}% -> {round(100 * b_refreshed.lvl / total_noise, 4)}%"
                            print(
                                f"\033[92mACESAlgebra.mult(a, b): `b` was successfully refreshed: {sat_evolution}.\033[0m"
                            )

                # Conclusion on refresh operations
                a_lvl = min(a.lvl, a_refreshed.lvl)
                b_lvl = min(b.lvl, b_refreshed.lvl)
                refreshed_noise = (a_lvl + b_lvl + a_lvl * b_lvl) * self.p + (
                    (self.p - 1) ** 2
                ) // self.p

                if self.debug:
                    sat_delta = f"saturation of {round(100 * noise / total_noise, 4)}% by \u0394 = {round(100 * (refreshed_noise - noise) / total_noise, 4)}%"
                    print(
                        f"\033[94mACESAlgebra.mult: refresh operation is to decrease {sat_delta}.\033[0m"
                    )

                if refreshed_noise / total_noise >= 0.99:
                    raise Exception(
                        f"ACESAlgebra.mult: refresh operation failed due to saturation at {round(100 * refreshed_noise / total_noise, 4)}%"
                    )

                return self.mult(
                    a_refreshed if a.lvl > a_refreshed.lvl else a,
                    b_refreshed if b.lvl > b_refreshed.lvl else b,
                    refresh=False,
                )

            else:
                raise Exception("ACESAlgebra.mult: noise cannot be refreshed.")

        # Addition on ACES ciphertexts
        c0 = []
        for k, lambda_k in enumerate(self.tensor):
            c0.append(b.enc * a.dec[k] + a.enc * b.dec[k])
            for i, a_dec_i in enumerate(a.dec):
                # Alternative 1: tmp_i = sum([Polynomial([lambda_k[i][j]],self.q) * b_dec_j for j, b_dec_j in enumerate(b.dec)], Polynomial([0],self.q))
                # Alternative 2: tmp_i = reduce(Polynomial.__add__, [Polynomial([lambda_k[i][j]], self.q) * b_dec_j for j, b_dec_j in enumerate(b.dec)])
                # Alternative 3 (below):
                tmp_i = Polynomial([0], self.q)
                for j, b_dec_j in enumerate(b.dec):
                    tmp_i = tmp_i + Polynomial([lambda_k[i][j]], self.q) * b_dec_j
                c0[-1] = c0[-1] - tmp_i * a_dec_i
            c0[-1] = c0[-1] % self.u
        c1 = (a.enc * b.enc) % self.u

        if self.debug:
            total_noise = (self.q + 1) // self.p - 1
            input_saturation = f"({round(100 * a.lvl / total_noise, 4)}%, {round(100 * b.lvl / total_noise, 4)}%)"
            output_saturation = f"{round(100 * noise / total_noise, 4)}%"
            print(
                f"\033[93mWarning in ACESAlgebra.mult: saturation increasing from {input_saturation} to {output_saturation} of max. noise level.\033[0m"
            )

        return ACESCipher(c0, c1, noise)

    def compile(self, instruction: str) -> Callable[[list[ACESCipher]], ACESCipher]:
        return lambda a: read_operations(self, instruction, a)

    def refresh(
        self,
        refresher: list[ACESCipher],
        corefresher: Tuple[list[ACESCipher], ACESCipher],
    ) -> ACESCipher:
        a, b = corefresher
        if self.debug and len(refresher) != len(a):
            print(
                "\033[93mWarning in ACESAlgebra.refresh: the refresher's length is not equal to the corefresher's length\033[0m"
            )
        return self.add(
            b,
            reduce(self.add, [self.mult(a[i], r_i) for i, r_i in enumerate(refresher)]),
        )

    def assess_refresh_level(
        self,
        refresher: list[ACESCipher],
        corefresher: Tuple[list[ACESCipher], ACESCipher],
    ) -> int:
        a, b = corefresher
        if self.debug and len(refresher) != len(a):
            print(
                "\033[93mWarning in ACESAlgebra.refresh: the refresher's length is not equal to the corefresher's length\033[0m"
            )
        xi = ((self.p - 1) + self.n * ((self.p - 1) ** 2)) // self.p
        return (
            xi
            + b.lvl
            + reduce(
                int.__add__,
                [
                    self.p * (a[i].lvl + r_i.lvl + a[i].lvl * r_i.lvl)
                    for i, r_i in enumerate(refresher)
                ],
            )
        )


class ACESRefreshClassifier(object):
    def __init__(self, ac: ArithChannel, debug: bool = False):
        self.p = ac.p
        self.q = ac.q
        self.n = ac.n
        self.x_images = ac.x_images
        self.debug = debug

    def is_refreshable(self, ciphertext: Union[ACESCipher, ACESPseudoCipher]) -> bool:
        if isinstance(ciphertext, ACESCipher):
            return self.is_refreshable(ciphertext.pseudo())
        iota = ciphertext.enc
        for i, x_i in enumerate(self.x_images):
            iota += ciphertext.dec[i] * x_i
        m_kp = iota % self.q
        k0p = (iota - m_kp) / self.q
        return (k0p % self.p) == 0

    def is_locator(self, dec: Union[list[Polynomial], list[int]]) -> Tuple[bool, float]:
        dec_ = [d(arg=1) if isinstance(d, Polynomial) else d for d in dec]
        iota_ = 0
        for i, x_i in enumerate(self.x_images):
            iota_ += dec_[i] * x_i
        x_barycenter = iota_ / self.q
        margin = x_barycenter - int(x_barycenter)
        k0p = sum(self.x_images) - int(x_barycenter)
        return (k0p % self.p) == 0, margin

    def is_director(self, dec: list[int]) -> Tuple[bool, float]:
        iota_ = 0
        for i, x_i in enumerate(self.x_images):
            iota_ += dec[i] * x_i
        x_barycenter = iota_ / self.q
        margin = x_barycenter - int(x_barycenter)
        k0p = int(x_barycenter)
        return (k0p % self.p) == 0, margin

    def refresh_classifier(
        self, ciphertext: Union[ACESCipher, ACESPseudoCipher]
    ) -> bool:
        is_locator, margin = self.is_locator(ciphertext.dec)

        max_margin = (ciphertext.lvl * self.p + self.p - 1) / self.q
        margin_condition = max_margin % self.p < 1 - margin

        if self.debug:
            print(
                "\t - margin condition satisfied:",
                margin_condition,
                "| margin:",
                margin,
            )
            print("\t - is locator", is_locator)
            if not (margin_condition) or not (is_locator):
                print(
                    "\033[91m\t - actual refreshability:",
                    self.is_refreshable(ciphertext),
                    "\033[0m",
                )

        return margin_condition and is_locator

    def find_affine(
        self,
        search_min: int,
        search_max: int,
        training_epochs: int,
        name: str = "default",
        file_option: Optional[str] = None,
    ) -> dict[str, Union[list[Tuple[list[int], float]], int]]:
        locators = set()
        directors = set()

        if file_option is not None:
            if file_option == "pickle":
                if os.path.exists(f".aces.classifier.{name}.pkl"):
                    with open(f".aces.classifier.{name}.pkl", "r") as f:
                        pickle_object = pickle.load(f)
                        locators = set(pickle_object["locators"])
                        directors = set(pickle_object["directors"])

            elif file_option == "json":
                if os.path.exists(f".aces.classifier.{name}.json"):
                    with open(f".aces.classifier.{name}.json", "r") as f:
                        json_object = json.load(f)
                        locators = set(json_object["locators"])
                        directors = set(json_object["directors"])

            else:
                print(
                    f"ACESRefreshClassifier.construct: Extension {file_option} non supported"
                )
                return None

        locators_length = len(locators)
        directors_length = len(directors)

        i = 0

        while i < training_epochs or len(directors) == 0 or len(locators) == 0:
            vector = [random.randint(search_min, search_max) for _ in range(self.n)]

            is_director, margin_dir = self.is_director(vector)[:2]
            if is_director:
                directors.add(str((vector, margin_dir)))

            is_locator, margin_loc = self.is_locator(vector)[:2]
            if is_locator:
                locators.add(str((vector, margin_loc)))

            i += 1

            if i > 10 * training_epochs:
                if len(directors) == 0 or len(locators) == 0:
                    print(
                        "ACESRefreshClassifier.construct: Failed to find affine structure."
                    )
                break

        update = {
            "locators": sorted(list(locators), reverse=True),
            "directors": sorted(list(directors), reverse=True),
            "p": self.p,
            "q": self.q,
        }

        update["locators"] = [eval(x) for x in update["locators"]]
        update["directors"] = [eval(x) for x in update["directors"]]

        print("added_locators:", len(locators) - locators_length)
        print("added_directors:", len(directors) - directors_length)

        if file_option is not None:
            if file_option == "pickle":
                with open(f".aces.classifier.{name}.pkl", "w") as f:
                    pickle.dump(update, f)

            elif file_option == "json":
                with open(f".aces.classifier.{name}.json", "w") as f:
                    json.dump(update, f, indent=2)

        return update


def refresh_classifier_generator(
    locators: list[Tuple[list[int], float]],
    directors: list[Tuple[list[int], float]],
    p: int,
    q: int,
    **args,
) -> Callable[[Union[ACESCipher, ACESPseudoCipher]], bool]:
    def refresh_classifier(ciphertext: Union[ACESCipher, ACESPseudoCipher]) -> bool:
        vector = np.array(
            [d(arg=1) if isinstance(d, Polynomial) else d for d in ciphertext.dec],
            dtype=int,
        )
        margin = []

        already_explored_vs = []
        already_explored_vs_counts = {"default": 0}
        already_explored_indices = []

        backtrack_vector = np.zeros(len(vector), dtype=int)

        while max(already_explored_vs_counts.values()) < len(vector):
            # Find the smallest non-zero coefficient index
            non_zero_indices = np.nonzero(vector)[0]
            if non_zero_indices.size == 0:
                break

            # Sort indices first by negativity, then by absolute value
            sorted_indices = non_zero_indices[
                np.lexsort(
                    (-np.abs(vector[non_zero_indices]), vector[non_zero_indices])
                )
            ][::-1]

            # Pick the first index that is not in the last indicies of previously_explored
            i = next(
                (
                    idx
                    for idx in sorted_indices
                    if idx not in already_explored_indices[-1:]
                ),
                None,
            )

            if i is None:  # All remaining indices are previously explored
                break

            already_explored_indices.append(i)

            # Find optimal locator (v, f)
            best_v, best_f, best_j = None, None, None
            for j, (v, f) in enumerate(directors):
                if j in already_explored_vs[-len(vector) :]:
                    continue

                v = np.array(v, dtype=int)
                if v[i] != 0 and v[i] == np.max(v):
                    if (
                        best_v is None
                        or abs(v[i]) < abs(best_v[i])
                        or (
                            abs(v[i]) == abs(best_v[i])
                            and np.count_nonzero(v) < np.count_nonzero(best_v)
                        )
                    ):
                        best_v, best_f, best_j = v, f, j

            if best_v is None or best_v[i] == 0:
                break

            already_explored_vs.append(best_j)
            already_explored_vs_counts.setdefault(best_j, 0)
            already_explored_vs_counts[best_j] += 1

            factor = vector[i] // best_v[i]

            vector -= factor * best_v
            backtrack_vector += factor * best_v
            margin.append(factor * best_f)

        print(vector)
        # Check if vector_ belongs to any director
        for v0, f0 in locators:
            v0_ = np.array(v0, dtype=int)
            if np.array_equal(vector, v0_):
                backtrack_vector += v0_

                margin.append(f0)
                margin_modulo = sum(margin) % p

                max_margin = (ciphertext.lvl * p + p - 1) / q
                margin_condition = max_margin % p < 1 - margin_modulo

                iota_homomorphism_condition = [r < q for r in backtrack_vector]

                return (
                    (margin_modulo < 1)
                    and margin_condition
                    and all(iota_homomorphism_condition)
                )

        return False

    return refresh_classifier
