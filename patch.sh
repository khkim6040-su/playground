#!/usr/bin/env bash

set -euo pipefail

usage() {
  echo "$0 - replace docker tag and staticdata version"
  echo " "
  echo "options:"
  echo " "
  echo "--work-dir                  [Required] target directory, ex) Deploy/eks/nk-dev-latest"
  echo "--docker-tag                [Optional] docker image tag for server, ex) main-badbadb"
  echo "--dedi-docker-tag           [Optional] unity dedicated server docker image, ex) release-dev-123456"
  echo "--static-data-version       [Optional] static data version, ex) ref:qa-latest, qa/123456"
  echo "--core-version-maps         [Optional] core version map, only value pairs ex) 133.6.11-05b-p1;133.8.1-05b-p1"
  echo "--data-pack-version-maps    [Optional] data pack version map, only value pairs ex) 615-04b;615-04b-p1"
}

# 123123.123;exit;

jq-inplace() {
  tmp=$(mktemp)
  jq "$@" > "$tmp" && mv "$tmp" "${@: -1}"
}

clear-core-version-map() {
  jq-inplace '.Client.ResourceHosts.CoreVersionMap = {}' a/appsettings.json
}

clear-data-pack-version-map() {
  jq-inplace '.Client.ResourceHosts.DataPackVersionMap = {}' a/appsettings.json
}

DOCKER_TAG=''
GANGAR_DOCKER_TAG=''
SERVER_STATICDATA_VERSION=''
CLIENT_STATICDATA_VERSION=''
CORE_VERSION_MAPS=''
DATA_PACK_VERSION_MAPS=''

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --work-dir)
      WORKDIR="$2"
      shift 2
      ;;
    --docker-tag)
      DOCKER_TAG="$2"
      shift 2
      ;;
    --dedi-docker-tag)
      GANGAR_DOCKER_TAG="$2"
      shift 2
      ;;
    --static-data-version)
      if [[ "$2" =~ ref:* ]]; then
        SERVER_STATICDATA_VERSION="$2"
        CLIENT_STATICDATA_VERSION="$2"
      elif [ -n "$2" ]; then
        SERVER_STATICDATA_VERSION="unity/$2"
        CLIENT_STATICDATA_VERSION="data/$2"
      fi
      shift 2
      ;;
    --core-version-maps)
      CORE_VERSION_MAPS="$2"
      shift 2
      ;;
    --data-pack-version-maps)
      DATA_PACK_VERSION_MAPS="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

pushd "$WORKDIR"

if [ -n "$DOCKER_TAG" ]; then
  for IMAGE_NAME in $(yq '.images[].name' kustomization.yaml); do
    if [ "$IMAGE_NAME" = 'gwanho-backend/gangar' ]; then
      continue
    fi
    kustomize edit set image "$IMAGE_NAME=*:$DOCKER_TAG"
  done
fi

if [ -n "$GANGAR_DOCKER_TAG" ]; then
  kustomize edit set image "gwanho-backend/gangar=*:$GANGAR_DOCKER_TAG"
fi

if [[ -n "$SERVER_STATICDATA_VERSION" ]]; then
  export SERVER_STATICDATA_VERSION;
  jq-inplace ".Server.S3.Version = env.SERVER_STATICDATA_VERSION" a/appsettings.json;
  jq-inplace ".Server.S3CompatibleOptions.Version = env.SERVER_STATICDATA_VERSION" b/appsettings.json;
  jq-inplace ".Server.S3.Version = env.SERVER_STATICDATA_VERSION" c/appsettings.json;
fi

if [[ -n "$CLIENT_STATICDATA_VERSION" ]]; then
  export CLIENT_STATICDATA_VERSION;
  jq-inplace ".Client.StaticData.Version = env.CLIENT_STATICDATA_VERSION" a/appsettings.json;
  [ ! -d d ] || jq-inplace ".Status.StaticData.Version = env.CLIENT_STATICDATA_VERSION" d/appsettings.json;
  [ ! -d simulation ] || yq -i '
  .spec.template.spec.containers[]
  |= select(.name == "app")
  |= .env[]
  |= select(.name == "WILLBEUPDATED")
  .value = strenv(CLIENT_STATICDATA_VERSION)
  ' simulation/deployment.yaml
  [ ! -d e ] || jq-inplace ".StaticDataOption.Version = env.CLIENT_STATICDATA_VERSION" e/appsettings.json;
fi

if [[ -n "$CORE_VERSION_MAPS" ]]; then
  clear-core-version-map
  jq-inplace '.Client.ResourceHosts.CoreVersionMap = {}' a/appsettings.json
  IFS=';' read -ra VALUES <<< "$CORE_VERSION_MAPS"
  # Extract key by splitting by first '-' and taking the first part
  for VALUE in "${VALUES[@]}"; do
    KEY="${VALUE%%-*}"
    jq-inplace --arg key "$KEY" --arg value "$VALUE"  '.Client.ResourceHosts.CoreVersionMap += { ($key) : $value }' a/appsettings.json
  done
fi

if [[ -n "$DATA_PACK_VERSION_MAPS" ]]; then
  clear-data-pack-version-map
  jq-inplace '.Client.ResourceHosts.DataPackVersionMap = {}' a/appsettings.json
  IFS=';' read -ra VALUES <<< "$DATA_PACK_VERSION_MAPS"
  # Extract key by splitting by first '-' and taking the first part
  for VALUE in "${VALUES[@]}"; do
    KEY="${VALUE%%-*}"
    jq-inplace --arg key "$KEY" --arg value "$VALUE"  '.Client.ResourceHosts.DataPackVersionMap += { ($key): $value }' a/appsettings.json
  done
fi

popd
