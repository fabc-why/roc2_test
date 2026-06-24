import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class AsyncSubscriber(Node):
    def __init__(self):
        super().__init__('async_subscriber')
        # 'async_topic' にデータが流れてきたら自動でコールバックを呼び出す設定
        self.subscription = self.create_subscription(
            String,
            'async_topic',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        # データを受信した瞬間に非同期に実行される
        self.get_logger().info(f'Received: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    node = AsyncSubscriber()
    rclpy.spin(node) # データが届くのを待ち続ける（ブロックせず裏でイベントを待機）
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
