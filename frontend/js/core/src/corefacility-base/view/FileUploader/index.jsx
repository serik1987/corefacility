import * as React from 'react';

import {NotImplementedError} from 'corefacility-base/exceptions/model';
import {HttpError} from 'corefacility-base/exceptions/network';

import styles from './style.module.css';


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
 * @param {callback} onError 			Triggers when file upload or delete raises an error.
 * @param {File|string|null} value 		If this prop is given, the widget is stated to
 * 										be in controllable mode. This props reflects the
 * 										value of the widget.
 * 										If this prop is omitted, the widget is stated to be in
 * 										uncontrollable mode.
 * @param {File|string} defaultValue	In uncontrollable mode defines value of the widget
 * 										after its first mounting.
 * @param {string} tooltip				The widget's tooltip.
 * @param {FileManager} fileManager		if this parameter was set, the following will happened:
 * 			onFileSelect prop will be ignored, FileManagers's upload() method will be called instead
 *			onFileRemove prop will be ignored, FileManager's delete() method will be called instead
 * 			value prop will be ignored, FileManager's value property will be used instead
 * 			when the FileManager is in progress, disabled is always treated as false, inactive is always
 * 			treated as true
 * @param {boolean} inactive			If true, the user can't change value of this widget
 * @param {boolean} loading 			If inactive is true, prints the 'Loading...' message below the uploader.
 * 										Otherwise, does nothing.
 * @param {boolean} readonly 			When the widget is read-only, "Upload" and "Delete" buttons are not shown.
 * 
 * State:
 * @param {File|string|null} value 		Value of the widget in uncontrollable mode.
 * 										Value of this state is useless in controllable mode.
 * @param {boolean} disabled			If true, the user can't change the value of this widget and
 * 										all controls look to be disabled
 * @param {boolean} inactive			if true, the user can't change value of this widget
 * @param {boolean} loading 			If inactive is true, prints the 'Loading...' message below the uploader.
 * 										Otherwise, does nothing.
 * inactive is true if either inactive state or inactive prop is true
 * loading is true if either loading state or loading prop is true
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

	RELOAD_STATUS_CODES = [401, 403, 404];

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

		this.state = {
			inactive: false,
			loading: false,
		}
		if (this.props.value === undefined && this.props.defaultValue !== undefined){
			this.state.value = this.props.defaultValue;
		} else {
			this.state.value = null;
		}
	}

	/** @{HTMLElement} parent's <div> element of the uploader */
	get htmlUploader(){
		return this.__ref.current;
	}

	/** Value to output */
	get value(){
		if (this.props.fileManager){
			return this.props.fileManager.value;
		}
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
				if (this.__fileToUrlMapping.url !== null){
					URL.revokeObjectURL(this.__fileToUrlMapping.url);
				}
				this.__fileToUrlMapping.url = URL.createObjectURL(this.value);
				this.__fileToUrlMapping.file = this.value;
			}
			return this.__fileToUrlMapping.url;
		}
	}

	/** the widget inactivity. Integrates information over state and props */
	get inactive(){
		return this.state.inactive || this.props.inactive;
	}

	/** the widget loading state. Integrates information over state and props */
	get loading(){
		return this.state.loading || this.props.loading;
	}

	/** The function evokes when dragging file enters the widget area
	 * 	@param {SyntheticEvent} event the dragging file
	 */
	handleDragEnter(event){
		if (this.props.disabled || this.inactive || this.props.readonly){
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
		if (this.props.disabled || this.inactive || this.props.readonly){
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
		this.setState({error: null});

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

	/** The function evokes when the file is gragging over the file uploader
	 * 	@param {SyntheticEvent} event 	the event to trigger
	 */
	handleDragOver(event){
		if (this.props.disabled || this.inactive || this.props.readonly){
			return;
		}
		event.preventDefault();
	}

	/** The function evokes when the file has been dropped to the file uploader
	 */
	handleDrop(event){
		this.setState({error: null});
		if (this.props.disabled || this.inactive || this.props.readonly){
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
	 * 	@async
	 * 	@param {object} event The event that triggered this function
	 * 	@return {undefined}
	 */
	async handleFileSelect(event){
		if (this.props.fileManager){
			await this.accessFileManager(manager => manager.upload(event.value));
		} else {
			this.setState({value: event.value});
			if (this.props.onFileSelect){
				this.props.onFileSelect(event);
			}
		}
	}

	/** The function evokes when the user presses "Delete" button.
	 * 	@async
	 * 	@param {object} event the event that triggered that function
	 * 	@return {undefined}
	 */
	async handleRemove(event){
		if (this.props.fileManager){
			await this.accessFileManager(manager => manager.delete());
		} else {
			this.setState({value: null});
			if (this.props.onFileRemove){
				this.props.onFileRemove(event);
			}
		}
	}

	/** Runs some function on the file manager
	 * 	@async
	 * 	@param {function} f 	The function to be executed
	 * 		@param {FileMAnager} manager 	Manages on which the function shall be executed
	 * 		@return {undefined}
	 * 	@return {undefined}
	 * 	
	 */
	async accessFileManager(f){
		try{
			this.setState({
				error: null,
				inactive: true,
				loading: true,
			});
			await f(this.props.fileManager);
			if (this.props.onError){
				this.props.onError(null);
			}
		} catch (error){
			this.handleError(error);
		} finally {
			this.setState({
				inactive: false,
				loading: false,
			});
		}
	}

	/** The function evokes when upload or delete response failed
	 * 	@param {Error} error the error that has been thrown
	 * 	@return {undefined}
	 */
	handleError(error){
		if (error instanceof HttpError && this.RELOAD_STATUS_CODES.indexOf(error.status) !== -1){
			window.location.reload();
		}
		if (this.props.onError){
			this.props.onError(error.message);
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