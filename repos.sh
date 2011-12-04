#!/bin/sh

case "$1" in
    "record" )
        git commit -a
        ;;
    "pull" )
        git pull origin master
        ;;
    "push" )
        git push git@github.com:manateelazycat/deepin-scrot.git
        ;;
    "revert" )
        git checkout -- .
        ;;
    * ) 
        echo "Help"
        echo "./repos.sh record         => record patch"
        echo "./repos.sh pull           => pull patch"
        echo "./repos.sh push           => push patch"
        echo "./repos.sh revert         => revert patch"
        ;;
    esac
