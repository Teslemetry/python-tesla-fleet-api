protoc -I=proto --python_out=pyi_out:tesla_fleet_api/tesla/vehicle/proto proto/*.proto
protol --create-package --in-place --python-out tesla_fleet_api/tesla/vehicle/proto protoc --proto-path=proto proto/*.proto
