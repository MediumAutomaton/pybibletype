# Tiny bargraph renderer for BibleType
# Version 1.0-0

class BargraphRenderer:
    def __init__(self):
        self.width = 80
        self.name = None

    def render(self, percentage):
        out = ""

        # Determine width of percentage bar, and draw name if applicable
        barWidth = self.width - 9
        if len(self.name) > barWidth - 5: # Shorten name if needed
            self.name = self.name[:barWidth-5]
        out += self.name + ": "
        barWidth -= len(self.name)

        # Draw percentage bar
        filledWidth = int(percentage * barWidth)
        percentBar = ("|" * filledWidth) + ("." * (barWidth - filledWidth))
        if len(percentBar) < barWidth:
            percentBar += "."
        out += percentBar + "* "

        # Draw numeric percentage
        if percentage == 1:
            out += " 100%"
        else:
            if percentage < 0.10:
                out += "0"
            out += str(round(percentage * 100, 1)) + "%"

        return out
