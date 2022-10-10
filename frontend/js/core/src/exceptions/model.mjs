export class ModelError extends Error{}


export class NotImplementedError extends ModelError{

    constructor(methodName){
        super(`The method ${methodName} has not been implemented. Probably, there is one of the following reasons: ` +
            `either you can create object from the abstract class or you did not implement all abstract methods.`);
    }

}

export class EntityPropertyError extends ModelError{

    constructor(entityName, propertyName){
        super(`The entity '${entityName}' has no property '${propertyName}'`);
    }

}


export class EntityStateError extends ModelError{

    constructor(entityState, action){
        super(`The action '${action}' is not allowed on the entity that is in state '${entityState}'`);
    }

}