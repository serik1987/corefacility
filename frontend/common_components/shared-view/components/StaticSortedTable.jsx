import * as React from 'react';

import SortedTable from './SortedTable';


/**
 * 	A table where the table data is sorted in fully offline mode, i.e., without any request to the Web Server.
 * 
 * 	The widget can work in fully controllable and fully uncontrollable modes. In fully uncontrollable mode the sorting
 * 	column is defined by the widget's state, in fully uncontrollable mode the sorting column is defined by the widget's
 * 	props. By default, the widget is in fully uncontrollable mode. To turn the widget into fully controllable mode
 * 	assign any value to the sortingColumn prop that is distinguished from undefined.
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
 * 	@param {String} 	sortingColumn 		A column along which the sorting has been performed. Setting this property
 * 											will turn the widget into fully controllable mode.
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
export default class StaticSortedTable extends React.Component{

	constructor(props){
		super(props);
		this.handleSortSelection = this.handleSortSelection.bind(this);

		this.state = {
			sortingColumn: null,
			order: null,
		}
	}

	render(){
		return (
			<SortedTable
				columns={this.props.columns}
				rows={this.props.rows}
				data={this._sortData()}
				sortable={this.props.sortable}
				sortingColumn={this.state.sortingColumn}
				order={this.state.order}
				onSortSelection={this.handleSortSelection}
			/>
		);
	}

	handleSortSelection(sortingColumn, order){
		this.setState({
			sortingColumn: sortingColumn,
			order: order,
		});
	}

	_sortData(){
		let data = [...this.props.data];
		let sortingIndex = this.props.columns.indexOf(this.state.sortingColumn);
		if (sortingIndex === -1){
			return data;
		}

		data.sort((row1, row2) => {
			let element1 = row1[sortingIndex];
			let element2 = row2[sortingIndex];
			let result = null;

			if (typeof element1 === 'number' && typeof element2 === 'number'){
				result = element1 - element2;
			} else {
				result = element1.toString().localeCompare(element2.toString());
			}

			if (this.state.order === 'desc'){
				result = -result;
			}

			return result;
		});

		return data;
	}

}