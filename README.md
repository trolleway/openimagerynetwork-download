# openimagerynetwork-download

# Deploy at Ubuntu 18.04

```
#Install Docker
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update
sudo apt install -y docker-ce

sudo usermod -aG docker ${USER}
su - ${USER}
id -nG

```

Using Docker 

```

docker build  github.com/trolleway/openimagerynetwork-download --no-cache --tag oadm

#create volume
docker volume create oadm_data

#mount with bind, for debug and filezilla
mkdir oadm_data
docker run -it  \
  --name oadm20 \
  --mount type=bind,source=$(pwd)/oadm_data,target=/openimagerynetwork-download/files \
  oadm
  
#mount with volume for production
docker run -it  \
  --name oadm20 \
  --mount type=volume,source=oadm_data,target=/openimagerynetwork-download/files \
  oadm
  
docker run --name=oadm20 -it -v ~/oadm_data:/files oadm 
docker attach

in container: python __main__.py --storage files --last 55  
  
#rm all
docker container stop oadm20
docker container rm oadm20
#or docker rm $(docker ps -a -q)

docker volume rm oadm_data

#To remove all unused volumes and free up space:s
docker volume prune
```

```
rm files/footprints.geojson
ogr2ogr -oo GEOM_POSSIBLE_NAMES=footprint -oo KEEP_GEOM_COLUMNS=NO -s_srs EPSG:4326 -t_srs EPSG:3857 files/footprints.geojson files/footprints.csv
```
