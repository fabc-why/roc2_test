import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import pygame
import sys

class JoyPublisher(Node):
    def __init__(self):
        super().__init__('joy_publisher')
        # データを送るパブリッシャーの作成
        self.publisher_ = self.create_publisher(Float32MultiArray, 'joy_states', 10)
        
        # Pygameとジョイスティックの初期化
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            self.get_logger().error("コントローラーが見つかりません。接続してください。")
            sys.exit(1)
            
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.get_logger().info(f"コントローラーを認識しました: {self.joystick.get_name()}")

        # 約30Hz (0.033秒ごと) に入力を読み込んで送信するタイマーを設定
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)

    def timer_callback(self):
        # Pygameの内部イベント状態を更新（これがないと値が更新されません）
        pygame.event.pump()

        # 1. 必要なデータを取得
        left_stick_x = self.joystick.get_axis(0)
        left_stick_y = self.joystick.get_axis(1)
        button_a = float(self.joystick.get_button(0)) # 0.0 か 1.0 に変換
        button_b = float(self.joystick.get_button(1))

        # 2. メッセージ型 (Float32MultiArray) にデータを詰める
        msg = Float32MultiArray()
        msg.data = [left_stick_x, left_stick_y, button_a, button_b]

        # 3. 非同期送信
        self.publisher_.publish(msg)
        
        # ログ出力（確認用）
        self.get_logger().info(
            f'Sent -> LX: {left_stick_x:.2f}, LY: {left_stick_y:.2f}, A: {int(button_a)}, B: {int(button_b)}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = JoyPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit() # Pygameの終了処理
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()