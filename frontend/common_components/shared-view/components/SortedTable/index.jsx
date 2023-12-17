import * as React from 'react';

import {ReactComponent as DropDownIcon} from '../../icons/dropdown_simple.svg';
import Table from '../Table';
import Hyperlink from '../Hyperlink';
import style from './style.module.css';


/**
 * 	This is a table where the sorting facility has been introduced.
 * 	Please, note that the sorting facility has not been implemented, it has been just introduced. This means that
 * 	the table has indeed clickable columns, clicking on columns indeed marks that the columns are sorted according
 * 	to given criteria but no actual sorting was provided.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Array|null}	columns				An array of column headers or null to skip printing the column headers.
 * 	@param {Array|null}	rows				An array of row headers or null to skip printing the row headers.
 * 	@param {Array}		data				A two-dimensional array of the table data. Each array inside this array
 * 											represents a single table row.
 * 	@param {function} 	onSortSelection		Triggers when the user changes the sorting column or the sort order.
 * 											The callback function has two arguments: a column selected by the user
 * 											and the sorted order specified by him.
 * 	@param {String} 	sortingColumn 		A column along which the sorting has been performed. The property turns
 * 											the system into fully controllable mode.
 * 	@param {String} 	order 				A sorting order. Allowed values: 'asc' and 'desc'. Useless for fully
 * 											uncontrollable mode.
 * 	@param {Array}		sortable 			List of columns along which sorting is possible. null or undefined means
 * 											that the sorting along each column is possible.
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {String} 	sortingColumn 		A column along which the sorting has been performed. Useless for fully
 * 											controllable mode.
 * 	@param {String} 	order 				A sorting order. Allowed values: 'asc' and 'desc'. Useless for fully
 * 											controllable mode.
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class SortedTable extends React.Component{

	constructor(props){
		super(props);

		this.state = {
			sortingColumn: null,
			order: null,
		}
	}

	/**
	 * 	Column along which the sorting has been performed
	 */
	get sortingColumn(){
		if (this.props.sortingColumn === undefined){
			return this.state.sortingColumn;
		} else {
			return this.props.sortingColumn;
		}
	}

	/**
	 * 	The sorting order
	 */
	get order(){
		if (this.state.sortingColumn === undefined){
			return this.state.order;
		} else {
			return this.props.order;
		}
	}

	render(){
		let columns = this.props.columns.map(column => {
			let columnIsSortable = this.props.sortable === null || this.props.sortable === undefined ||
				this.props.sortable.indexOf(column) !== -1;

			if (columnIsSortable){
				return (
					<div className={style.sorted_column}>
						<Hyperlink onClick={event => this.handleSort(column)}>{column}</Hyperlink>
						{this.sortingColumn === column && <span className={`${style.sorted_icon} ${this.order}`}>
							<DropDownIcon/>
						</span>}
					</div>
				);
			} else {
				return column;
			}
		});

		return (
			<Table
				columns={columns}
				rows={this.props.rows}
				data={this.props.data}
			/>
		);
	}

	handleSort(column){
		let desiredOrder = null;

		if (column === this.state.sortingColumn){
			if (this.state.order === 'desc'){
				desiredOrder = 'asc';
			} else {
				desiredOrder = 'desc';
			}
		} else {
			desiredOrder = 'desc';
		}

		this.setState({
			sortingColumn: column,
			order: desiredOrder,
		});
		if (this.props.onSortSelection){
			this.props.onSortSelection(column, desiredOrder);
		}
	}

}
