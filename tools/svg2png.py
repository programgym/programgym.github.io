import ctypes, sys, os

rsvg  = ctypes.CDLL("librsvg-2.so.2")
cairo = ctypes.CDLL("libcairo.so.2")
glib  = ctypes.CDLL("libglib-2.0.so.0")
gobj  = ctypes.CDLL("libgobject-2.0.so.0")

class RsvgDimensionData(ctypes.Structure):
    _fields_ = [("width", ctypes.c_int), ("height", ctypes.c_int),
                ("em", ctypes.c_double), ("ex", ctypes.c_double)]

rsvg.rsvg_handle_new_from_data.restype = ctypes.c_void_p
rsvg.rsvg_handle_new_from_data.argtypes = [ctypes.c_char_p, ctypes.c_size_t,
                                           ctypes.POINTER(ctypes.c_void_p)]
rsvg.rsvg_handle_get_dimensions.argtypes = [ctypes.c_void_p,
                                            ctypes.POINTER(RsvgDimensionData)]
rsvg.rsvg_handle_render_cairo.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
rsvg.rsvg_handle_render_cairo.restype = ctypes.c_int

cairo.cairo_image_surface_create.restype = ctypes.c_void_p
cairo.cairo_image_surface_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
cairo.cairo_create.restype = ctypes.c_void_p
cairo.cairo_create.argtypes = [ctypes.c_void_p]
cairo.cairo_scale.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double]
cairo.cairo_surface_write_to_png.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
cairo.cairo_surface_write_to_png.restype = ctypes.c_int
cairo.cairo_destroy.argtypes = [ctypes.c_void_p]
cairo.cairo_surface_destroy.argtypes = [ctypes.c_void_p]

FORMAT_ARGB32 = 0

def render(svg_path, out_path, target_px):
    data = open(svg_path, "rb").read()
    err = ctypes.c_void_p()
    h = rsvg.rsvg_handle_new_from_data(data, len(data), ctypes.byref(err))
    if not h:
        raise RuntimeError("rsvg failed to parse SVG")
    dim = RsvgDimensionData()
    rsvg.rsvg_handle_get_dimensions(h, ctypes.byref(dim))
    sw, sh = dim.width, dim.height
    scale = target_px / max(sw, sh)
    w, hgt = max(1, round(sw * scale)), max(1, round(sh * scale))
    surf = cairo.cairo_image_surface_create(FORMAT_ARGB32, w, hgt)
    cr = cairo.cairo_create(surf)
    cairo.cairo_scale(cr, w / sw, hgt / sh)
    ok = rsvg.rsvg_handle_render_cairo(h, cr)
    if not ok:
        raise RuntimeError("render_cairo returned FALSE")
    status = cairo.cairo_surface_write_to_png(surf, out_path.encode())
    cairo.cairo_destroy(cr); cairo.cairo_surface_destroy(surf)
    gobj.g_object_unref(ctypes.c_void_p(h))
    if status != 0:
        raise RuntimeError("write_to_png status %d" % status)
    print("%s  %dx%d  (source %dx%d)  %d bytes"
          % (out_path, w, hgt, sw, sh, os.path.getsize(out_path)))

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], int(sys.argv[3]))
