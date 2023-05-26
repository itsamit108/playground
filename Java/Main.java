import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JLabel;

public class Main {
    public static void main(String[] args) {
        JFrame frame = new JFrame("Label Example");
        ImageIcon icon = new ImageIcon("path_to_image.jpg");
        JLabel label = new JLabel("Hello, World!", icon, JLabel.CENTER);
        frame.add(label);
        frame.pack();
        frame.setVisible(true);
    }
}
