public class Main {
    public static void main(String[] args) {
        try {
            int[] arr = new int[3];
            arr[3] = 10;
        } catch (Exception e) {
            System.out.println("An exception occurred: " + e.getMessage());
        }
    }
}
