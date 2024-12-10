% This is a script to combine many different audio files into a single
% loop, used to make transcribing the files easier 


% Specify the folder containing the WAV files
folderPath = '/Users/montesinossl/Desktop/Color_Project/Color_Naming/color_naming/S06/';

% Get a list of all WAV files in the folder
filePattern = fullfile(folderPath, 'trial*.wav');
wavFiles = dir(filePattern);

% Sort the files based on the ending number
fileNumbers = cellfun(@(x) sscanf(x, 'trial%d.wav'), {wavFiles.name});
[~, sortingIndices] = sort(fileNumbers);

% Initialize an audio array to store concatenated audio
fullAudio = [];

% Loop through the files and concatenate the audio
for i = sortingIndices
    filePath = fullfile(folderPath, wavFiles(i).name);
    currentAudio = audioread(filePath);
    fullAudio = [fullAudio; currentAudio];
end

% Write the concatenated audio to a new WAV file
outputFilePath = '/Users/montesinossl/Desktop/Color_Project/Color_Naming/color_naming/S06/complete.wav';
audiowrite(outputFilePath, fullAudio, 44100);  % Assuming a sampling rate of 44100 Hz
disp('Concatenation complete!');
