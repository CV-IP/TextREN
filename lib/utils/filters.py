import logging
import numpy as np
import cv2
from PIL import Image


# Homomorphic filter class
class HomomorphicFilter:
    """Homomorphic filter implemented with diferents filters and an option to an external filter.

    High-frequency filters implemented:
        butterworth
        gaussian
    Attributes:
        a, b: Floats used on emphasis filter:
            H = a + b*H

        .
    """

    def __init__(self, a=0.5, b=1.5):
        self.a = float(a)
        self.b = float(b)

    # Filters
    def __butterworth_filter(self, I_shape, filter_params):
        P = I_shape[0] / 2
        Q = I_shape[1] / 2
        U, V = np.meshgrid(range(I_shape[0]), range(I_shape[1]), sparse=False, indexing='ij')
        Duv = (((U - P) ** 2 + (V - Q) ** 2)).astype(float)
        H = 1 / (1 + (Duv / filter_params[0] ** 2) ** filter_params[1])
        return (1 - H)

    def __gaussian_filter(self, I_shape, filter_params):
        P = I_shape[0] / 2
        Q = I_shape[1] / 2
        H = np.zeros(I_shape)
        U, V = np.meshgrid(range(I_shape[0]), range(I_shape[1]), sparse=False, indexing='ij')
        Duv = (((U - P) ** 2 + (V - Q) ** 2)).astype(float)
        H = np.exp((-Duv / (2 * (filter_params[0]) ** 2)))
        return (1 - H)

    # Methods
    def __apply_filter(self, I, H):
        H = np.fft.fftshift(H)
        I_filtered = (self.a + self.b * H) * I
        return I_filtered

    def filter(self, I, filter_params, filter='butterworth', H=None):
        """
        Method to apply homormophic filter on an image
        Attributes:
            I: Single channel image
            filter_params: Parameters to be used on filters:
                butterworth:
                    filter_params[0]: Cutoff frequency
                    filter_params[1]: Order of filter
                gaussian:
                    filter_params[0]: Cutoff frequency
            filter: Choose of the filter, options:
                butterworth
                gaussian
                external
            H: Used to pass external filter
        """

        #  Validating image
        if len(I.shape) is not 2:
            raise Exception('Improper image')

        # Take the image to log domain and then to frequency domain
        I_log = np.log1p(np.array(I, dtype="float"))
        I_fft = np.fft.fft2(I_log)

        # Filters
        if filter == 'butterworth':
            H = self.__butterworth_filter(I_shape=I_fft.shape, filter_params=filter_params)
        elif filter == 'gaussian':
            H = self.__gaussian_filter(I_shape=I_fft.shape, filter_params=filter_params)
        elif filter == 'external':
            print('external')
            if len(H.shape) is not 2:
                raise Exception('Invalid external filter')
        else:
            raise Exception('Selected filter not implemented')

        # Apply filter on frequency domain then take the image back to spatial domain
        I_fft_filt = self.__apply_filter(I=I_fft, H=H)
        I_filt = np.fft.ifft2(I_fft_filt)
        I = np.clip(np.exp(np.real(I_filt)) - 1, 0, 255)
        return np.uint8(I)

    def rgb_filter(self, img, filter_params=[30, 2]):
        img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
        dst_b = self.filter(img[:, :, 0], filter_params=[30, 2])
        dst_g = self.filter(img[:, :, 1], filter_params=[30, 2])
        dst_r = self.filter(img[:, :, 2], filter_params=[30, 2])
        dst = cv2.merge([dst_b, dst_g, dst_r])
        return Image.fromarray(cv2.cvtColor(dst, cv2.COLOR_BGR2RGB))

# End of class HomomorphicFilter

if __name__ == "__main__":
    import cv2

    # Code parameters
    path_in = './'
    path_out = './'
    img_path = 'error_20_from_airob_1.000.png'

    # Derived code parameters
    img_path_in = path_in + img_path
    img_path_out = path_out + 'filtered.png'

    # Main code
    img = Image.open(img_path_in).convert('RGB')
    homo_filter = HomomorphicFilter(a=0.75, b=1.25)
    img_filtered = homo_filter.rgb_filter(img)
    img_filtered.save('2.png')