import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst

# 初始化 GStreamer 库
Gst.init(None)

pipeline_str = 'v4l2src device=/dev/video0 ! video/x-raw,format=BGR,width=640,height=480 ! videoconvert ! appsink'

# 创建一个GStreamer管道
pipeline = Gst.parse_launch(pipeline_str)

# 获取appsink元素并注册回调函数
appsink = pipeline.get_by_name('appsink')


def on_new_sample(sink):
    sample = sink.emit('pull-sample')
    buf = sample.get_buffer()
    caps = sample.get_caps()
    data = buf.extract_dup(0, buf.get_size())
    W = caps.get_structure(0).get_value('width')
    H = caps.get_structure(0).get_value('height')
    return {'data': data, 'width': W, 'height': H}


appsink.set_property('emit-signals', True)
appsink.connect('new-sample', lambda s: on_new_sample(s))

# 启动管道
pipeline.set_state(Gst.State.PLAYING)

while True:
    # 获取一帧视频数据
    frame = on_new_sample(appsink)
    # TODO 处理数据

# 关闭管道
pipeline.set_state(Gst.State.NULL)
