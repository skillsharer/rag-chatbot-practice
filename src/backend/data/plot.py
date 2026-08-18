import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from src.config import SNAPSHOT_PATH


db = np.load(SNAPSHOT_PATH, allow_pickle=True).tolist()

vectors = np.array([
    entry["vector"]
    for entry in db
])

vectors_3d = PCA(n_components=3).fit_transform(vectors)

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

scatter = ax.scatter(
    vectors_3d[:, 0],
    vectors_3d[:, 1],
    vectors_3d[:, 2],
)

annotation = ax.annotate(
    "",
    xy=(0, 0),
    xytext=(10, 10),
    textcoords="offset points",
    bbox=dict(
        boxstyle="round,pad=0.5",
        facecolor="white",
        edgecolor="black",
        alpha=0.9,
    ),
)

annotation.set_visible(False)


def on_hover(event):
    if event.inaxes != ax:
        return

    contains, info = scatter.contains(event)

    if contains:
        idx = info["ind"][0]

        annotation.set_text(
            f"ID: {idx}\n\n"
            f"{db[idx]['text'][:300]}"
        )

        annotation.xy = (event.xdata, event.ydata)
        annotation.set_visible(True)
    else:
        annotation.set_visible(False)

    fig.canvas.draw_idle()


def on_scroll(event):
    if event.inaxes != ax:
        return

    scale = 0.9 if event.button == "up" else 1.1

    x_min, x_max = ax.get_xlim3d()
    y_min, y_max = ax.get_ylim3d()
    z_min, z_max = ax.get_zlim3d()

    def zoom_limits(min_val, max_val):
        center = (min_val + max_val) / 2
        half_range = (max_val - min_val) / 2 * scale
        return center - half_range, center + half_range

    ax.set_xlim3d(*zoom_limits(x_min, x_max))
    ax.set_ylim3d(*zoom_limits(y_min, y_max))
    ax.set_zlim3d(*zoom_limits(z_min, z_max))

    fig.canvas.draw_idle()


fig.canvas.mpl_connect("motion_notify_event", on_hover)
fig.canvas.mpl_connect("scroll_event", on_scroll)

ax.set_xlabel("PCA 1")
ax.set_ylabel("PCA 2")
ax.set_zlabel("PCA 3")
ax.set_title("Vector Database Embeddings")

plt.show()