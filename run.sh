#!/bin/bash
# Never print SECRET or TOKENS.

TARGET_DIR="/home/selery/runningrepo"
RESULTS_DIR="~/.openselery/results/"
RESULTS_DIR="${RESULTS_DIR/#\~/$HOME}"

if [ ! -d $RESULTS_DIR ]
then
    mkdir $RESULTS_DIR
fi
# Mount the argument folder into the container \
docker run --rm -t \
--env GITHUB_TOKEN=$GITHUB_TOKEN \
--env LIBRARIES_API_KEY=$LIBRARIES_API_KEY \
--env COINBASE_TOKEN=$COINBASE_TOKEN \
--env COINBASE_SECRET=$COINBASE_SECRET \
-v $@:$TARGET_DIR \
-v $(realpath $RESULTS_DIR):$(pwd)/results \
-u $(id -u $USER):$(id -g $USER) \
openselery \
--config $TARGET_DIR/selery.yml --directory $TARGET_DIR --result $TARGET_DIR/results


