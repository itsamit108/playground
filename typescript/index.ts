// Binary search

function binarySearch<T>(array: T[], value: T): number {
  let low = 0;
  let high = array.length - 1;

  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    const element = array[mid];

    if (element < value) {
      low = mid + 1;
    } else if (element > value) {
      high = mid - 1;
    } else {
      return mid;
    }
  }

  return -1;
}

const array = [1, 2, 3, 4, 5, 6, 7, 8, 9];
const value = 5;

console.log(binarySearch(array, value));
