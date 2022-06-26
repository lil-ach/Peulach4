
function buildNextElement(newElement, originalEle)
{
	matchAttributes(originalEle, newElement);
	let nextElement = null
	let newerElement = null	
	if (originalEle.children.length != 0)
	{
		nextElement = originalEle.firstElementChild;
		newerElement = document.createElement(nextElement.tagName);
		newElement.append(newerElement);
		buildNextElement(newerElement, nextElement);

	}
	if (originalEle.nextElementSibling != null)
	{
		nextElement = originalEle.nextElementSibling;
		newerElement = document.createElement(nextElement.tagName);
		newElement.after(newerElement);
		buildNextElement(newerElement, nextElement);
	}
}

function Add(elementid)
{
	let info = document.getElementById(elementid);
	if (info.childElementCount != 0)
	{	
		info = info.children[info.childElementCount-1];   
	}
	newElement = document.createElement(info.tagName);
	buildNextElement(newElement, info);
	console.log(newElement)
	info = document.getElementById(elementid);
	info.insertAdjacentElement("beforeend", newElement);
}

function matchAttributes(element1, element2)
{
	if (element1.attributes.length > 0)
	{
		let attributes = element1.getAttributeNames();
		for (i in attributes)
		{
			let newattr = element1.getAttribute(attributes[i]);
			if (attributes[i] == 'id' || attributes[i] == 'name')
			{
				let currattr = newattr.split('-');
				newattr = currattr[0] + "-" + (parseInt(currattr[1]) + 1);
			}
			element2.setAttribute(attributes[i], newattr);
		}
	}
}
