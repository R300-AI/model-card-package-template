$ErrorActionPreference = "Stop"
$imageName = if ($env:IMAGE_NAME) { $env:IMAGE_NAME } else { "model-cards.azurecr.io/example/cpu/echo-model-template:0.1.0" }
docker build -t $imageName .
