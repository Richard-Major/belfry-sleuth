# belfry-sleuth
A smart belfry monitor making use of an ADXL345 transducer through a Raspberry Pi.
With the transducer suitably fastened to the crown staple nut and the Pi suitably secured acceleration data is gathered from a ringing bell turning in the English style.
Code has been written to store the measured accelerations at 100 hz.
Data is collected during raising, ringing and lowering with pauses between activities used for mode detection.
Code has been produced to interpret the ringing section and measure to what extent the bell is odd struck.
