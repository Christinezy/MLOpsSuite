int cpp_code ( int n ) {
  int prev_prev = 1, prev = 2, curr = 3;
  while ( n ) {
    prev_prev = prev;
    prev = curr;
    curr = prev_prev + prev;
    n = n - ( curr - prev - 1 );
  }
  n = n + ( curr - prev - 1 );
  return prev + n;
}

