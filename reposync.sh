#!/bin/bash
 
# This script takes in the args that a hg push is given and checks for the paths
# that I've defined in my hg repos for either a push to bitbucket or github,
# and then does the other, so that regardless of which of these sites I push to
# the other also get pushed to.
 
#post-push to bitbucket
if [[ $HG_ARGS =~ "push bitbucket" ]]
then
    hg push github --quiet
fi
 
#post-push to github
if [[ $HG_ARGS =~ "push github" ]]
then
    hg push bitbucket --quiet
fi
