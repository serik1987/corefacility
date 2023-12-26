import * as React from 'react';

import {translate as t} from 'corefacility-base/utils';
import {NotImplementedError} from 'corefacility-base/exceptions/model';

import Icon from '../../shared-view/components/Icon';
import {ReactComponent as HandIcon} from '../../shared-view/icons/pan_tool.svg';
import {ReactComponent as ZoomInIcon} from '../../shared-view/icons/zoom_in.svg';
import {ReactComponent as ZoomOutIcon} from '../../shared-view/icons/zoom_out.svg';
import {ReactComponent as DefaultIcon} from '../../shared-view/icons/arrow_selection_tool.svg';

import style from './style.module.css';


/**
 * 	Implements necessary tools that are important for the chart control.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {any}		data 						The input data that shall be graphically represented
 * 	@param {boolean}	noRepaint					true - the chart will not be repainted after rendering
 * 														(suitable for multiple charts at a single page),
 * 													false - the chart will be repainted after rendering
 * 														(suitable for a single stand-alone chart).
 * 	@param {boolean}	visible						true - the chart will be visible (default value),
 * 													false - the chart will be hidden
 * 	@param {boolean}	followResize				true - repaint canvas automatically after the component resize
 * 													(default value),
 * 													false - this is the parent component that is responsible for the
 * 													resizing
 * 													Set this prop to true is there are multiple charts in the parent
 * 													component and the internal chart resizer work improperly. In this
 * 													case you must develop an external chart resizer.
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string} 	currentTool 				The tool selected by the user or null if none tool is selected
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class ChartToolbar extends React.Component{

	/**
	 * 	true if the user drags something, false otherwise
	 */
	_draggingMode = false;

	/**
	 * 	When the dragging mode is enabled, represents the mouse data at the coordinates starting
	 */
	_draggingStartContext = null;

	constructor(props){
		super(props);

		this.state = {
			...this.state,
			currentTool: null,
		}

		this.toolCursors = {
			hand: 'pointer',
		}
	}

	/**
	 * 	Renders the toolbar that allows to control the chart.
	 */
	renderToolbar(){
		return (
			<div className={`${style.toolbar} toolbar`}>
				<Icon
					tooltip={t("Cancel tool selection")}
					src={<DefaultIcon/>}
					onClick={event => this.selectTool(null)}
				/>
				<Icon
					tooltip={t("Zoom in")}
					src={<ZoomInIcon/>}
					onClick={event => this.changeScale(1.25)}
				/>
				<Icon
					tooltip={t("Zoom out")}
					src={<ZoomOutIcon/>}
					onClick={event => this.changeScale(0.8)}
				/>
				<Icon
					tooltip={t("Move")}
					src={<HandIcon/>}
					toggled={this.state.currentTool === 'hand'}
					onClick={event => this.selectTool('hand')}
				/>
			</div>
		)
	}

	render(){
		return <p><i>Please, implement the render() method.</i></p>;
	}

	/**
	 *  Changes the scale by a given factor
	 * 
	 * 	@abstract
	 * 	@param {Number} 		factor 		The new scale equals to the old scale multiplied by a given factor
	 */
	changeScale(factor){
		throw new NotImplementedError("ChartToolbar.changeScale has not been implemented.");
	}

	/**
	 * 	Triggers when the user starts moving the graph by means of 'hand' tool.
	 * 	"Starts moving the graph" means the the user presses the mouse button.
	 */
	startGraphMotion(){
		throw new NotImplementedError("chartToolbar.startGraphMotion has not been implemented.");
	}

	/**
	 * 	Triggers when the user continues moving the graph by means of 'hand' tool.
	 * 	"Continues moving the graph" means that the user move the mouse when its left button is hold.
	 * 
	 * 	@param {object} 		context 	Implementation-dependent information about the current position of the
	 * 										mouse cursor
	 */
	moveGraph(context){
		throw new NotImplementedError("chartToolbar.moveGraph has not been implemented.");
	}

	/**
	 * 	Triggers when the user finishes moving the graph by means of 'hand' tool.
	 * 	"Finishes moving the graph" means the the user releases the mouse button after he moved the graph to a given
	 * 	position
	 */
	finishGraphMotion(){
		throw new NotImplementedError("chartToolbar.finishGraphMotion has not been implemented.");
	}

	/**
	 * 	Selects a proper tool
	 * 
	 * 	@param {string|null}	toolName	Name of the tool to select or null to cancel the tool selection
	 */
	selectTool(toolName){
		this.setState({currentTool: toolName});
	}

	/**
	 * 	Triggers when the user clicks the mouse button.
	 * 	@param {ChartEvent}
	 */
	handleMouseEvents(event){
		switch (event.type){
		case 'mousedown':
			this._draggingMode = true;
			this._draggingStartContext = event.data;
			break;
		case 'mouseup':
			this._draggingMode = false;
			this._draggingStartContext = null;
		}

		switch (this.state.currentTool){
		case 'hand':
			this._applyHandTool(event);
			break;
		case null:
			break;
		default:
			this._applyCustomTool(this.state.currentTool, event);
		}
	}

	/**
	 * 	Applies the hand tool
	 * 
	 * 	@param {ChartEvent} 	event 				The triggered event
	 */
	_applyHandTool(event){
		switch (event.type){
		case 'mousedown':
			this.startGraphMotion();
			break;
		case 'mousemove':
			if (this._draggingMode){
				this.moveGraph(event.data);
			}
			break;
		case 'mouseup':
			this.finishGraphMotion();
			break;
		}
	}

	/**
	 * 	Applies the tool that is not embedded to the ChartToolbar (e.g., applies any tool except 'hand').
	 * 
	 * 	@param {string} 		tool 				Name of the tool used
	 * 	@param {ChartEvent} 	event 				The triggered event
	 */
	_applyCustomTool(tool, event){
		throw new NotImplementedError('ChartToolbar._applyTool: please, implement this method');
	}

}