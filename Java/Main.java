import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JFrame;
import javax.swing.JRadioButton;
import javax.swing.JToggleButton;

public class Main {
    public static void main(String[] args) {
        JFrame frame = new JFrame("Button Example");

        JButton button = new JButton("Click me!");
        JToggleButton toggleButton = new JToggleButton("Toggle");
        JCheckBox checkBox = new JCheckBox("Check me");
        JRadioButton radioButton = new JRadioButton("Select me");

        frame.add(button);
        frame.add(toggleButton);
        frame.add(checkBox);
        frame.add(radioButton);

        frame.setLayout(new FlowLayout()); // Set a layout manager
        frame.pack();
        frame.setVisible(true);
    }
}
