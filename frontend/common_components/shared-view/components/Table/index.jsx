import * as React from 'react';

import style from './style.module.css';



/**
 * 	Tables are highly suitable for representation of two-dimensional text data
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Array|null}	columns				An array of column headers or null to skip printing the column headers.
 * 	@param {Array|null}	rows				An array of row headers or null to skip printing the row headers.
 * 	@param {Array}		data				A two-dimensional array of the table data. Each array inside this array
 * 											represents a single table row.
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class Table extends React.Component{

	render(){
		let columnNumber = Math.max(...this.props.data.map(row => row.length));
		if (this.props.rows && this.props.rows.length > 0){
			columnNumber++;
		}
		let temporaryTableStyle = {
			gridTemplateColumns: `repeat(${columnNumber}, 1fr)`,
		}
		let temporaryHrStyle = {
			gridColumn: `span ${columnNumber}`,
		}

		return (
			<div className={`${style.table} table`} style={temporaryTableStyle}>
				{this.props.columns && this.props.columns.length && [
					this.props.rows && this.props.rows.length && <div className={`${style.cell}`}></div>,
					this.props.columns.map(columnHeader => {
						return (
							<div className={`${style.cell} ${style.header}`}>
								{columnHeader}
							</div>
						);
					}),
					<hr style={temporaryHrStyle}/>
				]}
				{this.props.data.map((row, index) => {
					return [
						this.props.rows && this.props.rows.length > 0 && (
							<div className={`${style.cell} ${style.row_header}`}>{this.props.rows[index]}</div>
						),
						row.map(cell => {
							return <div className={style.cell}>{cell}</div>;
						})
					];
				})}
			</div>
		);
	}

}