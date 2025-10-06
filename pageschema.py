class PageSpec:
    DPI = 300
    CUTS = {
        "A4":      (21.0, 29.7),
        "VAZIRI":   (17.0, 24.0),
        "ROGHI":    (14.0, 21.0),
        "JIBI":    (10.5, 14.8),
        "REHLI":    (21.0, 28.5),
        "KHESHTI":    (22.0, 21.5),
    }

    def __init__(self, cut_name="A4", font_pt=12, line_factor=1.2, direction="ltr"):
        if cut_name not in self.CUTS:
            raise ValueError(f"قطع '{cut_name}' تعریف نشده!")
        self.cut_name = cut_name
        self.font_pt = font_pt
        self.line_factor = line_factor
        self.direction = direction.lower()

        self.page_width, self.page_height = self._cm_to_px(*self.CUTS[cut_name])
        self.margins = self._calc_margins()
        self.line_spacing = self._calc_line_spacing()

    def _cm_to_px(self, w_cm, h_cm):
        inch_per_cm = 1 / 2.54
        return (
            round(w_cm * inch_per_cm * self.DPI),
            round(h_cm * inch_per_cm * self.DPI),
        )

    def _mm_to_px(self, mm):
        return round(mm * self.DPI / 25.4)

    def _calc_margins(self):
        # حدود استاندارد پیشنهادی
        mm_inner = 20  # چپ یا راست بسته به rtl/ltr
        mm_outer = 15
        mm_top   = 30
        mm_bottom= 20

        inner = self._mm_to_px(mm_inner)
        outer = self._mm_to_px(mm_outer)
        top   = self._mm_to_px(mm_top)
        bottom= self._mm_to_px(mm_bottom)

        if self.direction == "rtl":
            return {
                "left": outer,
                "right": inner,
                "top": top,
                "bottom": bottom,
            }
        else:  # ltr
            return {
                "left": inner,
                "right": outer,
                "top": top,
                "bottom": bottom,
            }

    def _calc_line_spacing(self):
        # یک pt = 1/72 inch
        px = (self.font_pt / 72) * self.DPI
        return round(px * self.line_factor)

    def spec(self):
        return {
            "PAGE_WIDTH": self.page_width,
            "PAGE_HEIGHT": self.page_height,
            "DISTANCE_LEFT": self.margins["left"],
            "DISTANCE_RIGHT": self.margins["right"],
            "DISTANCE_TOP": self.margins["top"],
            "DISTANCE_BOTTOM": self.margins["bottom"],
            "DISTANCE_LINE": self.line_spacing,
        }


# نمونه استفاده
if __name__ == "__main__":
    page = PageSpec(cut_name="A4", font_pt=12, line_factor=1.2, direction="rtl")
    print(page.spec())
