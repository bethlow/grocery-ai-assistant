% barcodeScanner.m
% Reads a barcode from an image file

function code = barcodeScanner(imageFile)
    % Read image
    img = imread(imageFile);

    % Detect barcode
    [code, barcodeType] = readBarcode(img);

    if isempty(code)
        disp('No barcode detected.');
        code = '';
    else
        fprintf('Barcode detected: %s (Type: %s)\n', code, barcodeType);
    end
end