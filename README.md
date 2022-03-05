# image tagger
 a simple script to tag and randomize images

usage : 
```
imageTagger.py <command> <-from <filename>> <-out <filename>> [-norename][-r] [amount]")
```
available commands: edit, tag, generate

edit can be used to manually edit image tags
tag can be used to automatically tag each image with a tag composed of parent folder
generate can be used to get all images with any of the specified tags and randomize them

tagging uses EXIF image metadata, the tag is Exif.Photo.UserComment, separated by spaces