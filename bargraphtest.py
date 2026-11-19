from bargraph import BargraphRenderer
bgRenderer = BargraphRenderer()

bgRenderer.name = input("Name:")
bgRenderer.width = int(input("Width:"))
bgRenderer.showPercent = True
percent = input("Show percent [y/n]?:") in ["y", "yes"]
if percent:
    bgRenderer.showPercent = True
else:
    bgRenderer.showPercent = False

print(bgRenderer.render(float(input("Percentage:"))))
