import * as React from 'react';

import {NotImplementedError} from '../../exceptions/model.mjs';
import styles from '../base-styles/FileUploader.module.css';


/** Base class for all widgets that can upload or delete the file.
 * 
 * The file uploader can work in two modes: 
 * 		Controllable mode - the widget is fully controlled by the parent.
 * 		Uncontrollable mode - the widget has its own internal state and doesn't
 * 							control by the parent.
 * 
 * Props:
 * @param {callback} onFileSelect		Triggers when the user selects certain file.
 * @param {callback} onFileRemove		Triggers when the user clears certain file.
 * @param {File|string|null} value 		If this prop is given, the widget is stated to
 * 										be in controllable mode. This props reflects the
 * 										value of the widget.
 * 										If this prop is omitted, the widget is stated to be in
 * 										uncontrollable mode.
 * @param {File|string} defaultValue	In uncontrollable mode defines value of the widget
 * 										after its first mounting.
 * @param {string} tooltip				The widget's tooltip.
 * 
 * State:
 * @param {File|string|null} value 		Value of the widget in uncontrollable mode.
 * 										Value of this state is useless in controllable mode.
 * 
 * Types of values:
 * 		File - the local client's file opened in the Web browser but still not uploaded.
 * 		string - the URL to the file that has already been uploaded to the Web server.
 * 		null - means that the widget contains no file.
 * 
 * 
 * Use the following values for the value state and value and defaultValue props:
 * 		1) when the file is available on the client (has not been uploaded), use File object
 * 		2) when the file is available on the server (has been uploaded) use string
 * 		3) when no file is attached, use null
 */
export default class FileUploader extends React.Component{

	constructor(props){
		super(props);
		this.handleUpload = this.handleUpload.bind(this);
		this.handleRemove = this.handleRemove.bind(this);
		this.handleDragEnter = this.handleDragEnter.bind(this);
		this.handleDragLeave = this.handleDragLeave.bind(this);
		this.handleDragOver = this.handleDragOver.bind(this);
		this.handleDrop = this.handleDrop.bind(this);

		this.__ref = React.createRef();
		this.__dragCounter = 0;
		this.__fileToUrlMapping = {
			file: null,
			url: null,
		}

		if (this.props.value === undefined && this.props.defaultValue !== undefined){
			this.state = {value: this.props.defaultValue};
		} else {
			this.state = {value: null};
		}
	}

	/** @{HTMLElement} parent's <div> element of the uploader */
	get htmlUploader(){
		return this.__ref.current;
	}

	/** Value to output */
	get value(){
		if (this.props.value !== undefined){ /* Controllable mode */
			return this.props.value;
		} else { /* Uncontrollable mode */
			return this.state.value;
		}
	}

	/** URL required for visual representation of the file */
	get valueUrl(){
		if (this.value === null || typeof this.value === "string"){
			return this.value;
		} else if (this.value instanceof File){
			if (this.value !== this.__fileToUrlMapping.file){
				console.log("Change URL");
				if (this.__fileToUrlMapping.url !== null){
					URL.revokeObjectURL(this.__fileToUrlMapping.url);
				}
				this.__fileToUrlMapping.url = URL.createObjectURL(this.value);
				this.__fileToUrlMapping.file = this.value;
			}
			return this.__fileToUrlMapping.url;
		}
	}

	/** The function evokes when dragging file enters the widget area
	 * 	@param {SyntheticEvent} event the dragging file
	 */
	handleDragEnter(event){
		if (this.props.disabled || this.props.inactive){
			return;
		}
		event.preventDefault();
		this.__dragCounter++;
		if (!this.htmlUploader.classList.contains(styles.dragging)){
			this.htmlUploader.classList.add(styles.dragging);
		}
	}

	/** The function evokes when dragging file leave the widget area
	 */
	handleDragLeave(event){
		if (this.props.disabled || this.props.inactive){
			return;
		}
		this.__dragCounter--;
		if (this.__dragCounter <= 0){
			this.__dragCounter = 0;
			if (this.htmlUploader.classList.contains(styles.dragging)){
				this.htmlUploader.classList.remove(styles.dragging);
			}
		}
	}

	/** The function must be called when the user clicks the 'Upload' button.
	 * 	@param {SyntheticEvent} event The event to be processed
	 */
	handleUpload(event){
		let self = this;

		let inputElement = document.createElement("input");
		inputElement.setAttribute("type", "file");
		inputElement.addEventListener("change", event => {
			self.handleFileSelect({
				value: event.target.files[0],
				target: {
					value: event.target.files[0],
				}
			});
		});
		inputElement.click();
	}

	handleRemove(event){
		this.setState({value: null});
		if (this.props.onFileRemove){
			this.props.onFileRemove(event);
		}
	}

	/** The function evokes when the file is gragging over the file uploader
	 * 	@param {SyntheticEvent} event 	the event to trigger
	 */
	handleDragOver(event){
		if (this.props.disabled || this.props.inactive){
			return;
		}
		event.preventDefault();
	}

	/** The function evokes when the file has been dropped to the file uploader
	 */
	handleDrop(event){
		if (this.props.disabled || this.props.inactive){
			return;
		}
		event.preventDefault();
		this.__dragCounter = 0;
		if (this.htmlUploader.classList.contains(styles.dragging)){
			this.htmlUploader.classList.remove(styles.dragging);
		}
		if (!event.dataTransfer || event.dataTransfer.items.length !== 1){
			return;
		}
		let item = event.dataTransfer.items[0];
		if (item.kind === "file"){
			event.value = event.target.value = item.getAsFile();
			this.handleFileSelect(event);
		}
	}

	/** The function evokes each time the user select a box using either
	 *  file drop or 'Upload' button.
	 */
	async handleFileSelect(event){
		this.setState({value: event.value});
		if (this.props.onFileSelect){
			this.props.onFileSelect(event);
		}
	}

	/** Renders internal content of the widget */
	renderContent(){
		throw new NotImplementedError("renderContent");
	}

	render(){
		this.__dragCounter = 0;

		return (
			<div
				title={this.props.tooltip}
				className={`${styles.file_container} file-container`}
				ref={this.__ref}
				onDragEnter={this.handleDragEnter}
				onDragLeave={this.handleDragLeave}
				onDragOver={this.handleDragOver}
				onDrop={this.handleDrop}
				>
					{this.renderContent()}
			</div>
		);
	}

}