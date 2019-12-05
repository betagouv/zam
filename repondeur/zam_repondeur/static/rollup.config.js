import hash from 'rollup-plugin-hash'

export default {
  input: 'js/zam.js',
  plugins: [
    hash({
      dest: 'js/build/zam.[hash].js',
      manifest: 'manifest.json',
      manifestKey: 'js/zam.js',
    })
  ],
  output: {
    file: 'js/build/zam.js',
    format: 'iife'
  }
}
