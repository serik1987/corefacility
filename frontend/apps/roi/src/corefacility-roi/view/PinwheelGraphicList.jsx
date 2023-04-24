import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as RoiToolIcon} from 'corefacility-base/shared-view/icons/variables.svg';
import RedirectionTool from 'corefacility-imaging/view/drawer_tools/RedirectionTool';

import GraphicList from './GraphicList';
import PinwheelAddTool from './drawer-tools/PinwheelAddTool';
import PinwheelEditTool from './drawer-tools/PinwheelEditTool';
import PinwheelRemoveTool from './drawer-tools/PinwheelRemoveTool';
import PinwheelDistanceTool from './drawer-tools/PinwheelDistanceTool';
import CloseAppTool from './drawer-tools/CloseAppTool';


/**
 * 	Allows the user to interactively manage the pinwheel list
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {FunctionalMap}	functionalMap 				The functional map to be downloaded.
 * 	@param {callback} 		onFetchStart 				Tells the parent component that the FunctionalMapDrawer starts
 * 														the map downloading. The callback requires no arguments.
 * 	@param {callback} 		onFetchSuccess 				Tells the parent component that the FunctionalMapDrawer
 * 														finishes the map downloading. The callback requires no arguments
 * 	@param {callback} 		onFetchFailure 				Tells the parent component that the FunctionalMapDrawer
 * 														was failed to download the map. Arguments:
 * 		@param {Error}			error 						A Javascript exception thrown during the map downloading.
 * 	@param {string}			cssSuffix 					Additional CSS clsaases to apply
 * 	@param {boolean} 		inactive 					All buttons and controls of this drawer are inactive
 * 	@param {Array} 			itemList 					List of all items to display
 * 	@param {callback} 		onItemAdd 					Triggers when the user tries to add new item. Asynchronous
 * 	@param {callback} 		onItemChange 				Triggers when the user tries to change the item. Asynchronous
 * 	@param {callback} 		onItemRemove				Triggers when the user tries to remove the item. Asynchronous
 *  @param {callback}       onPinwheelDistance          Triggers when the user tries to calculate the pinwheel distance.
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {BaseTool} 		currentTool					Currently selected tool
 * 	@param {Number} 		minValue 					Minimum amplitude
 * 	@param {Number} 		maxValue 					Maximum amplitude
 * 	@param {Number} 		colorBarResolution 			dimensions of the phase axis color bar, px
 * 	@param {Uint8ClampedArray} 	colorBarImage			bitmap for the phase axis color bar
 * 	@param {Number} 		scale 						Currently selected scale.
 * 	@param {String} 		redirect 					Route to redirect to or null if no redirection required
 * 	@param {Array} 			itemList 					List of all items to output
 * 
 */
export default class PinwheelGraphicList extends GraphicList{

    HALF_SQRT_3 = Math.sqrt(3) / 2;

    FILL_MARKER_TYPES = [];
    STROKE_MARKER_TYPES = ['star'];

    STAR_SIZE = 9;
    STAR_WIDTH = 1;
    CIRCLE_SIZE = 20;
    CIRCLE_START_ANGLE = 0;
    CIRCLE_FINISH_ANGLE = 2 * Math.PI;
    STAR_COLOR = {
        amplitude: "#ff0000",
        phase: "#000000",
    }
    CIRCLE_COLOR = {
        active: "rgba(255, 255, 255, 0.3)",
        usual: "rgba(255, 255, 255, 0.7)"
    };

    constructor(props){
        super(props);
        this._mapType = null;;
        this._cardinalLinePosition = null;
        this._diagonalLinePosition = null;
        this._markerType = null;

        this.tools = [
            ...this.tools,
            new PinwheelAddTool(),
            new PinwheelEditTool(),
            new PinwheelRemoveTool(),
            new PinwheelDistanceTool(),
            new RedirectionTool(t("Select rectangular ROI"), <RoiToolIcon/>, '/rectangular/'),
            new CloseAppTool(`/data/${this.props.functionalMap.id}/`),
        ];
    }

    repaintItems(){
        this._context.save();

        this._context.beginPath();
        this._context.rect(...this._getMapRectangle('phase'));
        this._context.clip();

        this._markerType = 'circle';
        this._mapType = 'phase';
        this._context.fillStyle = this.CIRCLE_COLOR.usual;
        this._circleRadius = Math.round(this.CIRCLE_SIZE / 2);
        this.repaintItemsPrimitive();

        this._markerType = 'circle-active';
        this._context.fillStyle = this.CIRCLE_COLOR.active;
        this.repaintItemsPrimitive();

        this._context.strokeStyle = this.STAR_COLOR.phase;
        this._markerType = 'star';
        this._cardinalLinePosition = Math.round(this.STAR_SIZE / 2);
        this._diagonalLinePosition = Math.round(this._cardinalLinePosition * this.HALF_SQRT_3);
        this.repaintItemsPrimitive();

        this._context.restore();
        this._context.save();

        this._context.beginPath();
        this._context.rect(...this._getMapRectangle('amplitude'));
        this._context.clip();

        this._context.strokeStyle = this.STAR_COLOR.amplitude;
        this._mapType = 'amplitude';
        this.repaintItemsPrimitive();

        this._context.restore();
    }

    repaintItemsPrimitive(){
        this._context.beginPath();
        super.repaintItems();
        if (this.STROKE_MARKER_TYPES.indexOf(this._markerType) !== -1){
            this._context.stroke();
        } else if (this.FILL_MARKER_TYPES.indexOf(this._markerType) !== -1){
            this._context.fill();
        }
    }

    /**
     *  Repaints a single item
     *  @param {Entity}     pinwheel                    Pinwheel to repaint
     *  @param {boolean}    isCurrent                   The item is currently selected by a given tool
     */
    repaintItem(pinwheel, isCurrent){
        let centerX = this.getCanvasX(pinwheel.x, this._mapType);
        let centerY = this.getCanvasY(pinwheel.y, this._mapType);

        switch (this._markerType){
        case 'star':
            this._context.moveTo(centerX - this._cardinalLinePosition, centerY + this.STAR_WIDTH / 2);
            this._context.lineTo(centerX + this._cardinalLinePosition + 1, centerY + this.STAR_WIDTH / 2);
            this._context.moveTo(centerX + this.STAR_WIDTH / 2, centerY - this._cardinalLinePosition);
            this._context.lineTo(centerX + this.STAR_WIDTH / 2, centerY + this._cardinalLinePosition + 1);
            this._context.moveTo(centerX - this._diagonalLinePosition, centerY - this._diagonalLinePosition);
            this._context.lineTo(centerX + this._diagonalLinePosition + 1, centerY + this._diagonalLinePosition + 1);
            this._context.moveTo(centerX - this._diagonalLinePosition, centerY + this._diagonalLinePosition + 1);
            this._context.lineTo(centerX + this._diagonalLinePosition + 1, centerY - this._diagonalLinePosition);
            break;
        case 'circle':
            if (!isCurrent){
                this._context.beginPath();
                this._context.arc(centerX, centerY, this._circleRadius,
                    this.CIRCLE_START_ANGLE, this.CIRCLE_FINISH_ANGLE);
                this._context.fill();
            }
            break;
        case 'circle-active':
            if (isCurrent){
                this._context.beginPath();
                this._context.arc(centerX, centerY, this._circleRadius,
                    this.CIRCLE_START_ANGLE, this.CIRCLE_FINISH_ANGLE);
                this._context.fill();
            }
            break;
        default:
            throw new Error("Unknown _markerType");
        }
        
    }
	
}