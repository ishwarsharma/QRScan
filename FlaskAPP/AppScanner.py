from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import rgba
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.camera import MDCamera
from android.permissions import request_permissions, Permission
from pyzbar import pyzbar
import ctypes.util
import ctypes

class CameraPreview(FloatLayout):
    def __init__(self, **kwargs):
        super(CameraPreview, self).__init__(**kwargs)
        self.camera = MDCamera(resolution=(1280, 720), play=True)
        self.camera.bind(on_texture=self.update)
        self.add_widget(self.camera)
        self.texture = None

        self.capture_btn = MDIconButton(icon='camera', pos_hint={'center_x':0.5, 'center_y':0.1})
        self.capture_btn.bind(on_press=self.capture)
        self.add_widget(self.capture_btn)

    def capture(self, instance):
        self.camera.export_to_png('qr_code.png')
        print('Image saved!')

    def update(self, camera, texture):
        if not self.texture:
            self.texture = texture
            self.texture_size = list(texture.size)
            Clock.schedule_interval(self.decode_qr_code, 1.0/30)

        self.texture.blit_buffer(texture.pixels, colorfmt='rgb')

    def decode_qr_code(self, dt):
        buffer = self.texture.pixels
        size = self.texture.size

        # Load the zbar library using ctypes
        zbar_dll = ctypes.cdll.LoadLibrary(ctypes.util.find_library('zbar'))
        zbar_dll.zbar_image_scanner_create.restype = ctypes.c_void_p
        zbar_dll.zbar_image_scanner_create.argtypes = []

        # Create a zbar image scanner
        scanner = zbar_dll.zbar_image_scanner_create()

        # Create a zbar image from the buffer
        zbar_image = zbar_dll.zbar_image_create()
        zbar_dll.zbar_image_set_format(zbar_image, ctypes.c_char_p(b'Y800'))
        zbar_dll.zbar_image_set_size(zbar_image, size[0], size[1])
        zbar_dll.zbar_image_set_data(zbar_image, buffer, size[0]*size[1], None)

        # Scan the image for barcodes
        zbar_dll.zbar_scan_image.restype = ctypes.c_int
        zbar_dll.zbar_scan_image.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        result = zbar_dll.zbar_scan_image(scanner, zbar_image)
        if result > 0:
            symbol = zbar_dll.zbar_image_first_symbol(zbar_image)
            while symbol:
                data = zbar_dll.zbar_symbol_get_data(symbol)

                # Print the barcode data and type
                print(f'Data: {data.decode("utf-8")}, Type: {symbol.type}')
                
                symbol = zbar_dll.zbar_symbol_next(symbol)

        zbar_dll.zbar_image_destroy(zbar_image)
        zbar_dll.zbar_image_scanner_destroy(scanner)

class QRCodeScannerApp(MDApp):
    def build(self):
        # Request camera permission
        request_permissions([Permission.CAMERA])
        return CameraPreview()

if __name__ == '__main__':
    QRCodeScannerApp().run()
