% imageProcessor.m
% Extracts simple color features from a grocery image

function features = imageProcessor(imageFile)
    % Read image
    img = imread(imageFile);

    % Resize for consistency
    img = imresize(img, [224 224]);

    % Extract mean color as a simple feature
    meanR = mean(mean(img(:,:,1)));
    meanG = mean(mean(img(:,:,2)));
    meanB = mean(mean(img(:,:,3)));

    features = [meanR, meanG, meanB];

    fprintf('Mean RGB: [%.2f, %.2f, %.2f]\n', features(1), features(2), features(3));
end