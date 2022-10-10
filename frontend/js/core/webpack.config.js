const path = require('path');

module.exports = {
	mode: 'development',
	entry: './src/main.mjs',
	output: {
		filename: 'main.min.js',
		path: path.resolve(__dirname, '../../../corefacility/core/static/core'),
	}
}