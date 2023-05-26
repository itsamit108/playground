import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

public class Main implements MouseListener, MouseMotionListener {

    private JFrame frame;
    private JPanel panel;

    public MouseEventDemo() {
        frame = new JFrame("Mouse Event Demo");
        panel = new JPanel();
        panel.addMouseListener(this);
        panel.addMouseMotionListener(this);
        frame.add(panel);
        frame.setSize(400, 300);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                new MouseEventDemo();
            }
        });
    }

    @Override
    public void mouseClicked(MouseEvent e) {
        System.out.println("Mouse Clicked");
    }

    @Override
    public void mousePressed(MouseEvent e) {
        System.out.println("Mouse Pressed");
    }

    @Override
    public void mouseReleased(MouseEvent e) {
        System.out.println("Mouse Released");
    }

    @Override
    public void mouseEntered(MouseEvent e) {
        System.out.println("Mouse Entered");
    }

    @Override
    public void mouseExited(MouseEvent e) {
        System.out.println("Mouse Exited");
    }

    @Override
    public void mouseDragged(MouseEvent e) {
        System.out.println("Mouse Dragged: X=" + e.getX() + ", Y=" + e.getY());
    }

    @Override
    public void mouseMoved(MouseEvent e) {
        System.out.println("Mouse Moved: X=" + e.getX() + ", Y=" + e.getY());
    }
}
