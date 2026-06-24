import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import sys

class JoySubscriber(Node):
    def __init__(self):
        super().__init__('joy_subscriber')
        self.subscription = self.create_subscription(
            Float32MultiArray,
            'joy_states',
            self.listener_callback,
            10)
        print("通信待機中... コントローラーを操作してください。")

    def listener_callback(self, msg):
        if len(msg.data) >= 4:
            lx = msg.data[0]
            ly = msg.data[1]
            btn_a = int(msg.data[2])
            btn_b = int(msg.data[3])
            
            # \r でカーソルを行頭に戻し、end='' で改行を防いで上書きする
            # ※ 前の文字が残らないように、末尾に少しスペースを空けてバッファを作ります
            print(f'\r[LIVE] Stick: ({lx:6.2f}, {ly:6.2f}) | A: {btn_a} | B: {btn_b}   ', end='')
            sys.stdout.flush() # 画面表示を即座に強制更新する

def main(args=None):
    rclpy.init(args=args)
    node = JoySubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\n終了します。") # 最後に改行を入れてターミナルを綺麗に戻す
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
