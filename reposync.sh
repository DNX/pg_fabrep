#!/bin/bash

#post-push to bitbucket
if [[ $HG_ARGS =~ "push bitbucket" ]]
then
    hg push github --quiet
fi
