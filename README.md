# OneShot Dialog Transcript
### Last updated 2021-01-19

This project extracts a transcript of all the dialog lines from the game [OneShot](http://www.oneshot-game.com/).

[View the transcript here](https://hunternet93.github.io/OneShot-Dialog-Transcript/dialog.html)

### Recreating the transcript

To recreate this transcript, use the following steps:

(note: these steps have only been tested on Linux)

1. Clone this repo and its submodule using Git.
2. From your own installation of OneShot, copy the `Data/Maps` and `Graphics/Faces` directories to the root of this repo.
3. Update the first line of `extractor.rb` to correctly reflect the number of `MapXXX.rxdata` files in the Maps directory.
4. Run the extractor with the command `ruby extractor.rb`. This will overwrite the `extracted.json` file with updated data.
5. Run the processor with the command `python3 process.py`. This will overwrite the `dialog.html` file with updated data.

# Copyright

The extracted text and character images are all copyright by OneShot's creators. They are used here for informational purposes only.