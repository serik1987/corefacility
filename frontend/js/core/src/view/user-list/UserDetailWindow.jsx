import React from 'react';
import {useParams} from 'react-router-dom';


class _UserDetailWindow extends React.Component{

	render(){
		return (<p>Looking for a user with ID={this.props.lookup}</p>);
	}

}


export default function UserDetailWindow(props){

	let {lookup} = useParams();

	return <_UserDetailWindow lookup={lookup} {...props} />

}