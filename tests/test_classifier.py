import sys 
sys.path.insert(1,"./")
import pyaces as pyc
import random

debug = True
loop_limit = 20

# the following will finish for the current parameters
while True:
    repartition = pyc.Repartition(n=5, p=2, upperbound=47601551)
    repartition.construct()
    ac = pyc.ArithChannel(p=4, N=10, deg_u=3, repartition=repartition)
    public = ac.publish(publish_levels=True)

    classifier = pyc.ACESRefreshClassifier(ac, debug=debug)
    data = classifier.find_affine(search_min=0, 
                                  search_max=2,
                                  training_epochs=2000)
    
    if data["locators"] == [] or data["directors"] == []:
        continue

    refresh_classifier = pyc.refresh_classifier_generator(**data)

    bob = pyc.ACES(**public, debug=debug)

    result = None
    count = 0
    while count < loop_limit:
        c = bob.encrypt(0)
        answer_without_secret_key = refresh_classifier(c)
        print("refreshability:", answer_without_secret_key)
        if answer_without_secret_key:
            result = answer_without_secret_key
            break
        count += 1
    
    if result is not None:
        break

answer_with_secret_key = classifier.refresh_classifier(c)
assert answer_with_secret_key == answer_without_secret_key
    

