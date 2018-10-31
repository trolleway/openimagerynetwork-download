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

z
su - ${USER}
id -nG

```

Using Docker 

```

cat > config.env << EOF
NEXTGISCOM_INSTANCE_URL=http://demo.nextgis.com
NEXTGISCOM_VECTOR_LAYER_ID=3029
NEXTGISCOM_LOGIN=administrator
NEXTGISCOM_PASSWORD=admin
EOF

docker build  github.com/trolleway/openimagerynetwork-download --no-cache --tag oadm

#create volume
docker volume create oadm_data

#mount with bind, for debug and filezilla
mkdir oadm_data
docker run -it  \
  --name oadm20 \
  --mount type=bind,source=$(pwd)/oadm_data,target=/openimagerynetwork-download/files \
  --env-file config.env \
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
создание слоя в ngw через api, потому что через веб-интерфейс он делает поля типа datetime, а с ними не работает мой скрипт синхронизации
```

{
"resource":{
    "cls":"vector_layer",
    "parent":{
        "id":0
    },
    "display_name":"Footprints",
    "keyname":null,
    "description":"Automatically updated by script openimagerynetwork-download"
},
"resmeta":{
    "items":{

    }
},
"vector_layer":{
    "srs":{ "id":3857 },
    "geometry_type": "MULTIPOLYGON",
    "fields": [
        {
            "keyname": "counter",
            "datatype": "STRING"
        },
                {
            "keyname": "uuid",
            "datatype": "STRING"
        },
                {
            "keyname": "title",
            "datatype": "STRING"
        },
                {
            "keyname": "gsd",
            "datatype": "STRING"
        },
                {
            "keyname": "file_size",
            "datatype": "STRING"
        },
                {
            "keyname": "platform",
            "datatype": "STRING"
        },
                {
            "keyname": "provider",
            "datatype": "STRING"
        },
                {
            "keyname": "contact",
            "datatype": "STRING"
        },
                        {
            "keyname": "properties.sensor",
            "datatype": "STRING"
        },
                        {
            "keyname": "properties.thumbnail",
            "datatype": "STRING"
        },
                        {
            "keyname": "properties.tms",
            "datatype": "STRING"
        },
                        {
            "keyname": "properties.wmts",
            "datatype": "STRING"
        },
                {
            "keyname": "uploaded_at",
            "datatype": "STRING"
        },
    ]
}
}


,,,,,,,,
```

