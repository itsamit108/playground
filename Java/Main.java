import javax.swing.*;
import java.awt.*;

public class MovingBanner extends JFrame {
    private JLabel bannerLabel;
    private int xCoordinate;
    private Timer timer;

    public MovingBanner() {
        setTitle("Moving Banner");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(400, 100);
        setResizable(false);
        setLocationRelativeTo(null);

        xCoordinate = getWidth();

        bannerLabel = new JLabel("Welcome to the Moving Banner!");
        bannerLabel.setFont(new Font("Arial", Font.BOLD, 20));
        bannerLabel.setForeground(Color.BLUE);
        bannerLabel.setHorizontalAlignment(SwingConstants.CENTER);
        add(bannerLabel);

        timer = new Timer(10, e -> {
            xCoordinate--;
            if (xCoordinate + bannerLabel.getWidth() < 0) {
                xCoordinate = getWidth();
            }
            bannerLabel.setLocation(xCoordinate, bannerLabel.getY());
        });
    }

    public void startAnimation() {
        timer.start();
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            MovingBanner banner = new MovingBanner();
            banner.setVisible(true);
            banner.startAnimation();
        });
    }
}
