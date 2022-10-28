import {NotImplementedError} from '../../exceptions/model.mjs';
import * as React from 'react';


/** This is a parent component for all dialog boxes (DialogBox instance).
 * 
 * 	Such classes as Window or Application are already subclasses of the
 * 	DialogWrapper class. So, methods defined here can be successfully
 * 	applied to these subclasses.
 * 	
 * 	The DialogWrapper manager dialog boxes and contains machinery for
 * 	their opening and closing, promise-based suspension of the task by
 * 	the time the user enters the data inside this dialog.
 * 
 * 	This is not a requirement that the opening component must be an instance of the
 * 	DialogWrapper. The only things required are to:
 * 	(1) accept 'dialogId' and 'options' props
 * 	(2) have openDialog async method
 */
export default class DialogWrapper extends React.Component{

	constructor(props){
		super(props);
		this.__modalInfo = [];
		this.__modalComponents = {};
		this.__registerModalComponent = this.__registerModalComponent.bind(this);
	}

	/** When you have been created the dialog box, you must register it in the parent
	 * 	DialogWrapper component. During the registration you let you Window or Application
	 * 	know that you have been create the dialog and intended to use it.
	 * 
	 * 	The method must be invoked inside the constructor. It will be worked improperly when
	 * 	it will be invoked everywhere else.
	 * 
	 * 	@param {string|Symbol} dialogId any arbitrary string or Symbol you ever wants. Different
	 * 		dialogs registered on the same DialogWrapper should have different dialog IDs.
	 * 
	 * 	@param {DialogBox} DialogComponent the dialog component to render
	 *
	 * 	@param {object} options some initial values that set as props of the dialog box.
	 * 		All values will be placed to a single options window.
	 */
	registerModal(dialogId, DialogComponent, options){
		if (dialogId in this.__modalInfo){
			throw new Error(`Another dialog box with ID ${dialogId} has already been registered. 
				Try another value as dialog box ID`);
		}
		options = options || {};
		this.__modalInfo.push({
			dialogId: dialogId,
			DialogComponent: DialogComponent,
			options: options
		});
	}

	/** This is a private method, don't invoke it! */
	__registerModalComponent(component){
		this.__modalComponents[component.props.dialogId] = component;
	}

	/** Renders all modal dialogs. This method must be invoked inside the render() method.
	 * 	@return {React.Component} path of the component tree to be appended to the component
	 * 		root element
	 */
	renderAllModals(){
		let self = this;

		return (<div>
			{this.__modalInfo.map(modalInfoElement => {
				let {dialogId, DialogComponent, options} = modalInfoElement;
				return (<DialogComponent
					dialogId={dialogId}
					options={options}
					ref={self.__registerModalComponent}/>);
			})}
		</div>);
	}

	/** Opens the modal box.
	 * 
	 *  @param {string} dialogId	the dialog ID that you have been passed during the invocation
	 * 		of the registerModal
	 * 	@param {any} inputData		The input data that will be passed to the modal window. These may
	 * 		be empty string, undefined or Entity you are going to change
	 * 
	 * 	@return {Promise} the method opens the dialog box and returns the promise. The promise will
	 * 		be fulfilled when the user closes the dialog box. If user cancels the operation, the promise
	 * 		will be fulfilled by false.
	 */
	async openModal(dialogId, inputData){
		let component = this.__modalComponents[dialogId];
		if (component.openDialog === undefined){
			return Promise.reject(new TypeError(`The component registered in the dialog wrapper with ID='${dialogId}' doesn't have openDialog method.`));
		}
		return component.openDialog(inputData);
	}

	/** Renders the window.
	 *  @abstract
	 */
	render(){
		throw new NotImplementedError("render");
		return null;
	}

}