protoc -I=protobuf --python_out=pyi_out:tesla_fleet_api/pb2 protobuf/*.proto
protol --create-package --in-place --python-out tesla_fleet_api/pb2 protoc --proto-path=protobuf protobuf/*.proto
