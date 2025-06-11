from scipy.spatial import distance as dist

def get_aspect_ratio(top, bottom, right, left):
    height = dist.euclidean([top.x, top.y], [bottom.x, bottom.y])
    width = dist.euclidean([right.x, right.y], [left.x, left.y])
    return height / width

def timeout_double(state, frames, WAIT_FRAMES):
    if state:
        frames += 1
    if frames > WAIT_FRAMES:
        frames = 0
        state = False
    return state, frames