PROTOC_VERSION=31.1

protoc --version
curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v$PROTOC_VERSION/protoc-$PROTOC_VERSION-linux-x86_64.zip
sudo unzip -o protoc-$PROTOC_VERSION-linux-x86_64.zip -d /usr/local bin/protoc
sudo unzip -o protoc-$PROTOC_VERSION-linux-x86_64.zip -d /usr/local 'include/*'
rm protoc-$PROTOC_VERSION-linux-x86_64.zip
protoc --version
