int n; int i; int sum; int a[5];
n = 5; i = 0; sum = 0;
while (i < n) {
  a[i] = i * 2;
  sum = sum + a[i];
  i = i + 1;
}
if (sum > 10) { print(true); } else { print(false); }
print(sum);
