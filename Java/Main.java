// Bubbl sort
class BubbleSort{
    public static void main(String[] args) {
        int[] arr = {5, 1, 4, 2, 8};
        int temp = 0;
        for(int i = 0; i < arr.length; i++){
            for(int j = 1; j < (arr.length - i); j++){
                if(arr[j - 1] > arr[j]){
                    temp = arr[j - 1];
                    arr[j - 1] = arr[j];
                    arr[j] = temp;
                }
            }
        }
        for(int i = 0; i < arr.length; i++){
            System.out.print(arr[i] + " ");
        }
    }
}

class Main{
public static void main(String[] args) {
    System.out.println("Hello World!");
    BubbleSort.main(args);
    }
}
