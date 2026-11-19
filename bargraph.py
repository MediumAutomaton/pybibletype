# Bargraph renderer
# Version 1.0-0

class BargraphRenderingError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class BargraphRenderer:
    def __init__(self,
                 width = 80,
                 showPercent = False,
                 filledChar = "|",
                 unfilledChar = ".",
                 endChar = "*",
                 name = None):
        self.width = width
        self.showPercent = showPercent
        self.filledChar = filledChar
        self.unfilledChar = unfilledChar
        self.endChar = endChar
        self.name = name

    def render(self, percentage):
        # Sanity checks
        if len(self.filledChar) != 1 or len(self.unfilledChar) != 1:
            raise BargraphRenderingError("Length of filledChar and unfilledChar must be exactly 1")
        if (self.showPercent and self.width < 12 + len(self.endChar)) or (not self.showPercent and self.width < 6 + len(self.endChar)):
            raise BargraphRenderingError("Width must be at least 12 + endChar length with percentage or at least 6 + endChar length without percentage")
        if percentage < 0 or percentage > 1:
            raise BargraphRenderingError("Percentage must be between 0 and 1 inclusive")

        out = ""

        # Determine width of percentage bar, and draw name if applicable
        barWidth = self.width - len(self.endChar)
        if self.showPercent:
            barWidth -= 6
        if self.name:
            if len(self.name) > barWidth - 5: # Shorten name if needed
                self.name = self.name[:barWidth-5]
            out += self.name + ": "
            barWidth -= len(self.name) + 2

        # Draw percentage bar
        filledWidth = int(percentage * barWidth)
        percentBar = self.filledChar * filledWidth
        percentBar += self.unfilledChar * (barWidth - filledWidth)
        if len(percentBar) < barWidth:
            percentBar += self.unfilledChar
        out += percentBar + self.endChar

        # Draw numeric percentage
        if self.showPercent:
            out += " "
            if percentage == 1:
                out += " 100%"
            else:
                if percentage < 0.10:
                    out += "0"
                out += str(round(percentage * 100, 1)) + "%"

        return out
